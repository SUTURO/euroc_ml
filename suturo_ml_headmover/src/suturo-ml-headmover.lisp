(in-package :exec)

(defvar *yaml-pub*)
(defparameter red-sphere-start-pose (make-msg "geometry_msgs/Pose" 
                                              (:W :ORIENTATION) 1
                                              (:X :ORIENTATION) 0
                                              (:Y :ORIENTATION) 0
                                              (:Y :ORIENTATION) 0
                                              (:X :POSITION) 0
                                              (:Y :POSITION) 0.5
                                              (:Z :POSITION) 0.04))
(defparameter red-cube-start-pose (make-msg "geometry_msgs/Pose" 
                                            (:W :ORIENTATION) 1
                                            (:X :ORIENTATION) 0
                                            (:Y :ORIENTATION) 0
                                            (:Y :ORIENTATION) 0
                                            (:X :POSITION) -0.3
                                            (:Y :POSITION) -0.4
                                            (:Z :POSITION) 0.03))
(defparameter blue-handle-start-pose (make-msg "geometry_msgs/Pose" 
                                               (:W :ORIENTATION) 1
                                               (:X :ORIENTATION) 0
                                               (:Y :ORIENTATION) 0
                                               (:Y :ORIENTATION) 0
                                               (:X :POSITION) 0
                                               (:Y :POSITION) 0.5
                                               (:Z :POSITION) 0.01))
(defun parse-yaml ()
  "Subscribes the yaml publisher and sets environment:*yaml* to stay informed about changes"
  ; TODO: Publish the yaml description to the yaml pars0r input
  (roslisp:subscribe constants:+topic-name-get-yaml+ 'suturo_msgs-msg:Task #'yaml-cb))

(defun yaml-publisher ()
  "Creates the publisher for the yaml-file"
  (setf *yaml-pub* (advertise "/suturo/startup/yaml_pars0r_input" "std_msgs/String")))

(roslisp-utilities:register-ros-init-function parse-yaml)
(roslisp-utilities:register-ros-init-function yaml-publisher)

(defmacro with-process-modules (&body body)
  "Macro to define the used process modules."
  `(cpm:with-process-modules-running
       (suturo-planning-pm-manipulation
        suturo-planning-pm-perception)
     ,@body))

(defmacro with-ros-node (&body body)
  "Utility macro to start and stop a ROS node around a block"
  `(unwind-protect
    (progn
      (roslisp-utilities:startup-ros)
      ,@body)
    (roslisp-utilities:shutdown-ros)))

(defun publish-objects-to-collision-scene ()
  (loop for object across (msg-slot-value environment::*yaml* 'objects) do
    (let ((start-pose (cond 
                        ((string= (msg-slot-value object 'name) "red_sphere") red-sphere-start-pose)
                        ((string= (msg-slot-value object 'name) "red_cube") red-cube-start-pose)
                        ((string= (msg-slot-value object 'name) "blue_handle") blue-handle-start-pose)))
          (primitive-poses '())) 
      (loop for primitive-pose across (msg-slot-value object 'primitive_poses) do
        (if (not (string= (msg-slot-value object 'name) "red_sphere"))
        (push (make-msg "geometry_msgs/Pose" 
                        :ORIENTATION (msg-slot-value start-pose 'orientation) 
                        :POSITION (point+ (msg-slot-value start-pose 'position) (msg-slot-value primitive-pose 'position))) primitive-poses))
      (format t "~a" primitive-poses)
      (manipulation::publish-collision-object (msg-slot-value object 'name) (msg-slot-value object 'primitives) (make-array (list (length primitive-poses)) 
                                                                                                                            :initial-contents (reverse primitive-poses)) 0)))))

(defun point+ (p1 p2)
"Adds two gemeotry_msgs/Point and returns the solution
* Arguments
- p1 :: The first point as geometry_msgs/Point
- p2 :: The second point as geometry_msgs/Point
* Return
The sum of the point as geometry_msgs/Point
"
  (make-msg "geometry_msgs/Point" :x (+ (msg-slot-value p1 'x) (msg-slot-value p2 'x)) 
                                  :y (+ (msg-slot-value p1 'y) (msg-slot-value p2 'y)) 
                                  :z (+ (msg-slot-value p1 'z) (msg-slot-value p2 'z))))

(defun task-selector ()
  "Starts the plan for the task from the parameter server.

   If no task is set in the parameter server, the task given
   as argument will be started (default: task1_v1)"
  (with-ros-node
    (let ((tsk (get-param "/task_variation" "head_mover")))
      (unless (wait-for-service +service-name-start-simulator+ +timeout-service+)
        (ros-error (task-selector) "Service ~a timed out." +service-name-start-simulator+)
        (fail))
      (ros-info (task-selector) "Starting simulator...")
      (let* ((ret (call-service +service-name-start-simulator+
                                            'euroc_c2_msgs-srv:StartSimulator
                                            :user_id "suturo"
                                            :scene_name tsk))
             (_ (ros-info (task-selector) "Task starter return: ~a" ret))
             (task-description (slot-value ret 'euroc_c2_msgs-srv:description_yaml)))
        (publish-msg *yaml-pub* :data task-description)
        (let ((task (remove #\  (get-param "/task_description/public_description/task_name" tsk)))) ; whitespace sensitive!
          (ros-info (task-selector) "Starting plan ~a..." task)
          (unwind-protect
            (print "funcall")
            (defparameter my-task task)
            (funcall (symbol-function (read-from-string (format nil "exec:~a" task))))
            (print "funcall done")
            (when cram-beliefstate::*logging-enabled*
              (ros-info (task-selector) "Saving log files...")
              (cram-beliefstate:extract-files))))))))

(def-top-level-cram-function head_mover ()
  "Top level plan for task 1 of the euroc challenge"
  (print "FUUUU BAR")
  (sleep 60)
  (manipulation:init)
  (publish-objects-to-collision-scene)
  (with-process-modules
    (with-retry-counters ((all-retry-count 2)
                          (inform-objects-retry-count 2)
                          (objects-in-place-retry-count 3))
      (with-failure-handling
          ((simple-plan-failure (e)
             (declare (ignore e))
             (ros-warn (toplevel head_mover) "Something failed.")
             (do-retry all-retry-count
               (ros-warn (toplevel head_mover) "Retrying all.")
             (reset-counter inform-objects-retry-count)
               (reset-counter objects-in-place-retry-count)
               (retry))))
          (with-failure-handling
              ((objects-information-failed (e)
                 (declare (ignore e))
                 (ros-warn (toplevel head_mover) "Failed to inform objects.")
                 (do-retry inform-objects-retry-count
                   (ros-warn (toplevel head_mover) "Retrying.")
                   (retry))))
            (let ((objects (achieve '(objects-informed))))
              (with-failure-handling
                  (((or objects-in-place-failed
                        cram-plan-failures:manipulation-failure) (e)
                     (declare (ignore e))
                     (ros-warn (toplevel head_mover) "Failed to put objects in place.")
                     (do-retry objects-in-place-retry-count
                       (ros-warn (toplevel head_mover) "Retrying.")
                       (retry))))
                (achieve `(objects-in-place ,objects)))))))))

(defun yaml-cb (msg)
  "
Callback for the function [[parse-yaml]]. Sets the variable environment:*yaml*.
"
  (setf environment:*yaml* msg))

(def-goal (achieve (grab-top ?object))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
)

(def-goal (achieve (grab-side ?object))
" 
Grabs the given object from the side
* Arguments
- ?objects :: The object that should be grabed
"
)

(def-goal (achieve (place-in-zone ?object))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
)

(def-goal (achieve (open-gripper ?object))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
)


(def-goal (achieve (turn ?object))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
)

(defun call-service-state (service-name taskdata)
  "
Calls the service of the given service-name. Every state service has to accept an object of suturo_startup_msgs-srv:TaskDataService.
* Arguments
- service-name :: The name of a state service has to start with suturo/startup/. This argument needs the last part of the service name e.g: suturo/startup/myAwesomeService -> myAwesomeService.
- taskdata :: The suturo_startup_msgs-msgs:Taskdata object that should be send to the service
"
  (let
      ((full-service-name (concatenate 'string "suturo/startup/" service-name)))
    (print (concatenate 'string "calling service: " service-name))
    (if (not (roslisp:wait-for-service full-service-name +timeout-service+))
        (progn
          (let 
              ((timed-out-text (concatenate 'string "Timed out waiting for service " service-name)))
            (roslisp:ros-warn nil t timed-out-text))
          nil)
        (let ((value (roslisp:call-service full-service-name 'suturo_startup_msgs-srv:TaskDataService :taskdata taskdata)))
          (roslisp:msg-slot-value value 'result)))))

(def-cram-function init-simulation (task_name)
  "
Initialize the simulation:
- Start simulation
- Start manipulation
- Start perception
- Start classifier
"
  (let ((taskdata (roslisp:make-msg "suturo_startup_msgs/TaskData" (name) task_name)))
    (call-service-state "start_simulation" taskdata)
    (call-service-state "start_manipulation" taskdata)
    (call-service-state "init" taskdata)) 
  (publish-objects-to-collision-scene))

(defun call-prolog-next-solution(id)
  "* Arguments 
- id :: The ID of the object which solution should be found
* Return Value
 Returns a list with two elements. The first is a number with:
 - 0 :: No solution found 
 - 1 :: wrong id
 - 2 :: query failed
 - 3 :: done
 - 4 :: service timed out
 The second element is the found solution
* Description
 TODO "
  (let ((result '()))
    (if (not (roslisp:wait-for-service "json_prolog/next_solution" +timeout-service+))
        (progn 
          (print "Prolog next solution timed out")
          (setf result '(4 "")))
        (setf result (roslisp:call-service "json_prolog/next_solution" 'json_prolog_msgs-srv:PrologNextSolution :id id)))
    `(,(msg-slot-value result 'status) ,(msg-slot-value result 'solution))))

(defun try-solutions (object)
  (do ((result '(0 "")))
      ((= (first result) 3) (first result))
    (setf result (call-prolog-next-solution (msg-slot-value object 'name)))
    (cond 
      ((= (first result) 0) (print "No solution found"))
      ((= (first result) 1) (print "Wrong id"))
      ((= (first result) 2) (print "Query failed"))
      ((= (first result) 4) (print "Timed out"))
      ((= (first result) 3) 
       (cond
         ((string= (second result) "grab-top") (achieve `(grap-top ,object)))
         ((string= (second result) "grab-side") (achieve `(grap-side ,object)))
         ((string= (second result) "turn") (achieve `(turn ,object)))
         ((string= (second result) "open-gripper") (achieve `(open-gripper ,object)))
         ((string= (second result) "place-in-zone") (achieve `(place-in-zone ,object))))))))
               
