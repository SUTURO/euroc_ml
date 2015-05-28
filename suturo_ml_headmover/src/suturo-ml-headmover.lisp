(in-package :exec)

(defvar *yaml-pub*)
(defparameter red-sphere-pose `#(,(make-msg "geometry_msgs/Pose" 
                                   (:W :ORIENTATION) 1
                                   (:X :ORIENTATION) 0
                                   (:Y :ORIENTATION) 0
                                   (:Y :ORIENTATION) 0
                                   (:X :POSITION) 0
                                   (:Y :POSITION) 0.5
                                   (:Z :POSITION) 0.1)))
(defparameter red-cube-pose `#(,(make-msg "geometry_msgs/Pose" 
                                (:W :ORIENTATION) 1
                                (:X :ORIENTATION) 0
                                (:Y :ORIENTATION) 0
                                (:Y :ORIENTATION) 0
                                (:X :POSITION) -0.3
                                (:Y :POSITION) -0.4
                                (:Z :POSITION) 0.03)))
(defparameter blue-handle-pose `#(,(make-msg "geometry_msgs/Pose" 
                              (:W :ORIENTATION) 1
                              (:X :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:X :POSITION) 0
                              (:Y :POSITION) 0.5
                              (:Z :POSITION) 0.03)
                            ,(make-msg "geometry_msgs/Pose" 
                              (:W :ORIENTATION) 1
                              (:X :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:X :POSITION) (+ 0 0.0275)
                              (:Y :POSITION) (+ 0.5 0.0025)
                              (:Z :POSITION) (+ 0.03 0.0225))
                            ,(make-msg "geometry_msgs/Pose" 
                              (:W :ORIENTATION) 1
                              (:X :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:X :POSITION) (+ 0 -0.0275)
                              (:Y :POSITION) (+ 0.5 -0.0025)
                              (:Z :POSITION) (+ 0.03 0.0225))
                            ,(make-msg "geometry_msgs/Pose" 
                              (:W :ORIENTATION) 1
                              (:X :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:X :POSITION) (+ 0 -0.0025)
                              (:Y :POSITION) (+ 0.5 0.0275)
                              (:Z :POSITION) (+ 0.03 0.0225))
                            ,(make-msg "geometry_msgs/Pose" 
                              (:W :ORIENTATION) 1
                              (:X :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:Y :ORIENTATION) 0
                              (:X :POSITION) (+ 0 0.0025)
                              (:Y :POSITION) (+ 0.5 -0.0275)
                              (:Z :POSITION) (+ 0.03 0.0225))))
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

(defun publish-objects-to-collision-scene()
  (loop for object across (msg-slot-value environment::*yaml* 'objects) do
    (let ((primitive-poses (cond 
                            ((string= (msg-slot-value object 'name) "red_sphere") red-sphere-pose)
                            ((string= (msg-slot-value object 'name) "red_cube") red-cube-pose)
                            ((string= (msg-slot-value object 'name) "blue_handle") blue-handle-pose))))
    (manipulation::publish-collision-object (msg-slot-value object 'name) (msg-slot-value object 'primitives) primitive-poses 0))))

(defun task-selector ()
  "Starts the plan for the task from the parameter server.

   If no task is set in the parameter server, the task given
   as argument will be started (default: task1_v1)"
  (with-ros-node
    (let ((tsk (get-param "/task_variation" "task1_v1")))
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
  (manipulation:init)
  (with-process-modules
    (with-retry-counters ((all-retry-count 2)
                          (inform-objects-retry-count 2)
                          (objects-in-place-retry-count 3))
      (with-failure-handling
          ((simple-plan-failure (e)
             (declare (ignore e))
             (ros-warn (toplevel task1) "Something failed.")
             (do-retry all-retry-count
               (ros-warn (toplevel task1) "Retrying all.")
             (reset-counter inform-objects-retry-count)
               (reset-counter objects-in-place-retry-count)
               (retry))))
          (with-failure-handling
              ((objects-information-failed (e)
                 (declare (ignore e))
                 (ros-warn (toplevel task1) "Failed to inform objects.")
                 (do-retry inform-objects-retry-count
                   (ros-warn (toplevel task1) "Retrying.")
                   (retry))))
            (let ((objects (achieve '(objects-informed))))
              (with-failure-handling
                  (((or objects-in-place-failed
                        cram-plan-failures:manipulation-failure) (e)
                     (declare (ignore e))
                     (ros-warn (toplevel task1) "Failed to put objects in place.")
                     (do-retry objects-in-place-retry-count
                       (ros-warn (toplevel task1) "Retrying.")
                       (retry))))
                (achieve `(objects-in-place ,objects)))))))))

(defun yaml-cb (msg)
  "
Callback for the function [[parse-yaml]]. Sets the variable environment:*yaml*.
"
  (setf environment:*yaml* msg))

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
  (manipulation:init))
