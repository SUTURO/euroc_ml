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
(defparameter red-cube nil)
(defparameter red-cube-collision nil)
(defparameter red-cube-object-desig nil)
(defparameter blue-handle nil)
(defparameter blue-handle-collision nil)
(defparameter blue-handle-object-desig nil)
(defparameter last-object-grabbed "")

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
  "TODO SIMPLIFY CAUSE COLLISION OBJEKT IS ALREADY THERE"
  (loop for object across (msg-slot-value environment::*yaml* 'objects) do
    (let ((start-pose nil)
          (primitive-poses '()))
      (cond 
        ((string= (msg-slot-value object 'name) "red_sphere") (setf start-pose red-sphere-start-pose))
        ((string= (msg-slot-value object 'name) "red_cube") (setf start-pose red-cube-start-pose))
        ((string= (msg-slot-value object 'name) "blue_handle") (setf start-pose blue-handle-start-pose)))
      (loop for primitive-pose across (msg-slot-value object 'primitive_poses) do
        (if (not (string= (msg-slot-value object 'name) "red_sphere"))
            (push (make-msg "geometry_msgs/Pose" 
                        :ORIENTATION (msg-slot-value start-pose 'orientation) 
                        :POSITION (point+ (msg-slot-value start-pose 'position) (msg-slot-value primitive-pose 'position))) primitive-poses)))
        (manipulation::publish-collision-object (msg-slot-value object 'name) 
                                                (msg-slot-value object 'primitives) 
                                                (make-array (list (length primitive-poses) 
                                                                  :initial-contents (reverse primitive-poses)))0))))

(defun publish-head-mover-scene ()
  (manipulation::publish-collision-object "blue_handle"
                                          `#(,(roslisp:make-msg 
                                             "shape_msgs/SolidPrimitive" 
                                             (type) 1 
                                             (dimensions) #(0.048 0.048 0.12)) )
                                          `#(,(roslisp:make-msg 
                                             "geometry_msgs/Pose" 
                                             (position) (roslisp:make-msg 
                                                         "geometry_msgs/Point" 
                                                         (x) 0.0 (y) 0.5 (z) 0.06)
                                             (orientation) (roslisp:make-msg 
                                                            "geometry_msgs/Quaternion" 
                                                            (x) 0.0 (y) 0.0 (z) 0.0 (w) 1.0)))
                                          0)
  (manipulation::publish-collision-object "red_cube"
                                          `#(,(roslisp:make-msg 
                                             "shape_msgs/SolidPrimitive" 
                                             (type) 1 
                                             (dimensions) #(0.05 0.05 0.05)) )
                                          `#(,(roslisp:make-msg 
                                             "geometry_msgs/Pose" 
                                             (position) (roslisp:make-msg 
                                                         "geometry_msgs/Point" 
                                                         (x) -0.3 (y) -0.4 (z) 0.0)
                                             (orientation) (roslisp:make-msg 
                                                            "geometry_msgs/Quaternion" 
                                                            (x) 0.0 (y) 0.0 (z) 0.0 (w) 1.0)))
                                          0))

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
  (init-exec)

  (with-process-modules
    (execute-prolog-solutions)))

(defun yaml-cb (msg)
  "
Callback for the function [[parse-yaml]]. Sets the variable environment:*yaml*.
"
  (setf environment:*yaml* msg))

(defparameter bla nil)
(def-goal (achieve (grab-top ?object))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
  (print "GRABBING_TOP")
  (setf bla ?object)
  (let ((new-desig (copy-designator ?object :new-description `((prefer-grasp-position 1))))) 
    (equate ?object new-desig))
  (perform (make-designator 'action `((to grasp)
                                      (obj ,?object))))
  (setf last-object-grabbed (msg-slot-value (desig-prop-value ?object 'cram-designator-properties:collision-object) 'id)))


(def-goal (achieve (grab-side ?object))
" 
Grabs the given object from the side
* Arguments
- ?objects :: The object that should be grabed
"
  (print "GRABBING_SIDE")
  (let ((new-desig (copy-designator ?object :new-description `((prefer-grasp-position 2))))) 
    (equate ?object new-desig))
  (perform (make-designator 'action `((to grasp)
                                      (obj ,?object))))
  (setf last-object-grabbed (msg-slot-value (desig-prop-value ?object 'cram-designator-properties:collision-object) 'id)))

(def-goal (achieve (place-in-zone))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
  (print "PLACING IN ZONE")
  (let ((object-grabbed
          (cond 
            ((string= last-object-grabbed "red_cube") red-cube-object-desig)
            ((string= last-object-grabbed "blue_handle") blue-handle-object-desig)
            (t nil))))
    (if object-grabbed
        (let ((target-location (make-designator 'location `((pose ,(cl-tf:make-pose-stamped 
          (msg-slot-value (msg-slot-value (desig-prop-value (current-desig object-grabbed) 'cram-designator-properties:target-zone) 'HEADER) 'FRAME_ID)
          (ros-time) 
          (cl-transforms:make-3d-vector 
           (msg-slot-value (msg-slot-value (msg-slot-value (desig-prop-value (current-desig object-grabbed) 'cram-designator-properties:target-zone) 'POSE) 'POSITION) 'X)
           (msg-slot-value (msg-slot-value (msg-slot-value (desig-prop-value (current-desig object-grabbed) 'cram-designator-properties:target-zone) 'POSE) 'POSITION) 'Y)
           (msg-slot-value (msg-slot-value (msg-slot-value (desig-prop-value (current-desig object-grabbed) 'cram-designator-properties:target-zone) 'POSE) 'POSITION) 'Z))
          (cl-transforms:make-quaternion 
           (msg-slot-value (msg-slot-value (msg-slot-value (desig-prop-value (current-desig object-grabbed) 'cram-designator-properties:target-zone) 'POSE) 'ORIENTATION) 'X)
           (msg-slot-value (msg-slot-value (msg-slot-value (desig-prop-value (current-desig object-grabbed) 'cram-designator-properties:target-zone) 'POSE) 'ORIENTATION) 'Y)
           (msg-slot-value (msg-slot-value (msg-slot-value (desig-prop-value (current-desig object-grabbed) 'cram-designator-properties:target-zone) 'POSE) 'ORIENTATION) 'Z)
           (msg-slot-value (msg-slot-value (msg-slot-value (desig-prop-value (current-desig object-grabbed) 'cram-designator-properties:target-zone) 'POSE) 'ORIENTATION) 'W))
))))))

          (perform (make-designator 'action `((to put-down)
                                              (obj ,(current-desig object-grabbed))
                                              (at ,target-location))))))))
        

(def-goal (achieve (open-gripper))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
  (print "OPENING GRIPPER")
)


(def-goal (achieve (turn))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
  (print "TURNING")
)

(defun init-exec()
  (init-exec-collision-scene)
  (init-exec-params)
  (init-exec-object-designators))


(defun init-exec-collision-scene()
  "Initialises the collision scene"
  (let ((result (manipulation::init)))
    (loop
      (setf result (manipulation:init))
      (wait-duration 1)
      (when (not (eql (msg-slot-value result 'subscriber-connections) nil))
        (return)))
    (publish-objects-to-collision-scene)))

(defun init-exec-params()
  (loop for object across (msg-slot-value environment::*yaml* 'objects) do
    (let ((start-pose nil)
          (primitive-poses '()))
      (cond 
        ((string= (msg-slot-value object 'name) "red_cube") 
         (progn
          (setf start-pose red-cube-start-pose)
          (setf red-cube object)))
        ((string= (msg-slot-value object 'name) "blue_handle") 
         (progn
           (setf start-pose blue-handle-start-pose)
           (setf blue-handle object))))
      (if start-pose
          (progn
            (loop for primitive-pose across (msg-slot-value object 'primitive_poses) do
              (push (make-msg "geometry_msgs/Pose" 
                              :ORIENTATION (msg-slot-value start-pose 'orientation) 
                              :POSITION (point+ (msg-slot-value start-pose 'position) (msg-slot-value primitive-pose 'position))) primitive-poses))
            (cond 
              ((string= (msg-slot-value object 'name) "red_cube") (setf red-cube-collision  
                                                                        (make-msg "moveit_msgs/CollisionObject" 
                                                                                  :ID (msg-slot-value object 'name)
                                                                                  :PRIMITIVES (msg-slot-value object 'primitives)
                                                                                  :PRIMITIVE_POSES (make-array (list (length primitive-poses))
                                                                                                               :initial-contents (reverse primitive-poses))
                                                                                  :OPERATION 0
                                                                                  (:FRAME_ID :HEADER) "/map"
                                                                                  (:STAMP :HEADER) (roslisp:ros-time) 
                                                                                  (:SEQ :HEADER) 0))) 
              ((string= (msg-slot-value object 'name) "blue_handle") (setf blue-handle-collision  
                                                                        (make-msg "moveit_msgs/CollisionObject" 
                                                                                  :ID (msg-slot-value object 'name)
                                                                                  :PRIMITIVES (msg-slot-value object 'primitives)
                                                                                  :PRIMITIVE_POSES (make-array (list (length primitive-poses))
                                                                                                               :initial-contents (reverse primitive-poses))
                                                                                  :OPERATION 0
                                                                                  (:FRAME_ID :HEADER) "/map"
                                                                                  (:STAMP :HEADER) (roslisp:ros-time) 
                                                                                  (:SEQ :HEADER) 0)))))))))
(defun init-exec-object-designators ()
  (loop for zone across (msg-slot-value environment::*yaml* 'target_zones) do
      (cond 
        ((string= (msg-slot-value zone 'expected_object) "red_cube") (setf red-cube-object-desig
                                                                            (make-designator 'object 
                                                                                             `((collision-object ,red-cube-collision)
                                                                                               (target-zone ,(make-msg "geometry_msgs/PoseStamped"
                                                                                                                       (:FRAME_ID :HEADER) "/map"
                                                                                                                       (:STAMP :HEADER) (roslisp:ros-time) 
                                                                                                                       (:SEQ :HEADER) 0
                                                                                                                      :pose (make-msg "geometry_msgs/Pose"
                                                                                                                                      (:W :ORIENTATION) 1
                                                                                                                                      (:X :ORIENTATION) 0
                                                                                                                                      (:Y :ORIENTATION) 0
                                                                                                                                      (:Y :ORIENTATION) 0
                                                                                                                                      :POSITION (msg-slot-value zone 'target_position))))))))
        ((string= (msg-slot-value zone 'expected_object) "blue_handle") (setf blue-handle-object-desig
                                                                            (make-designator 'object 
                                                                                             `((collision-object ,blue-handle-collision)
                                                                                               (target-zone ,(make-msg "geometry_msgs/PoseStamped"
                                                                                                                       (:FRAME_ID :HEADER) "/map"
                                                                                                                       (:STAMP :HEADER) (roslisp:ros-time) 
                                                                                                                       (:SEQ :HEADER) 0
                                                                                                                      :pose (make-msg "geometry_msgs/Pose"
                                                                                                                                      (:W :ORIENTATION) 1
                                                                                                                                      (:X :ORIENTATION) 0
                                                                                                                                      (:Y :ORIENTATION) 0
                                                                                                                                      (:Y :ORIENTATION) 0
                                                                                                                                      :POSITION (msg-slot-value zone 'target_position))))))))

   ))) 
  
                

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


(defun execute-prolog-solutions()
  ""
  (let ((goals (first (first (json-prolog:prolog-simple-1 "get_planned_goals(G)")))))
    (loop for goal in goals do
      (if (typep goal 'list) 
          (try-solution goal)))))
  
(defun try-solution (query)
  (let ((object nil))
    (cond
      ((eql (second query) CL-USER::'|'red_cube'|) (setf object red-cube-object-desig))
      ((eql (second query) CL-USER::'|'blue_handle'|) (setf object blue-handle-object-desig)))
    (cond
      ((eql (first query) CL-USER::'|'top_grab'|) (achieve `(grab-top ,object)))
      ((eql (first query) CL-USER::'|'side_grab'|) (achieve `(grab-side ,object)))
      ((eql (first query) CL-USER::'|'turn'|) (achieve `(turn)))
      ((eql (first query) CL-USER::'|'open_gripper'|) (achieve `(open-gripper)))
      ((eql (first query) CL-USER::'|'place_in_zone'|) (achieve `(place-in-zone)))
      (t (print "No matching goal found")))))

(defun grasp-top (object)
  "
  Grasp the given object and lift it
  * Arguments
  - object-designator :: The designator describing the object - object-designator
  "
  (let ((collision-object object))
    (if (not (roslisp:wait-for-service +service-name-grasp-object+ +timeout-service+))
        (let ((timed-out-text (concatenate 'string "Times out waiting for service" +service-name-grasp-object+)))
          (roslisp:ros-warn nil t timed-out-text)
          (cpl-impl:fail 'cram-plan-failures:manipulation-failure))
        (progn
          (let* ((response (roslisp:call-service +service-name-grasp-object+ 
                                                 'suturo_manipulation_msgs-srv:GraspObject
                                                 :object (roslisp:setf-msg collision-object 
                                                                           (stamp header) 
                                                                           (roslisp:ros-time))
                                                 :density (manipulation::get-object-density collision-object 
                                                                                            (roslisp:msg-slot-value environment:*yaml* 'objects)) 
                                                 :prefer_grasp_position 2))
                 (result (roslisp:msg-slot-value response 'result))
                 (grasp-position (roslisp:msg-slot-value response 'grasp_position))))))))


