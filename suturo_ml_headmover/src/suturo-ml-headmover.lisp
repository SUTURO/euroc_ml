(in-package :exec)
"""FEATURES IN MSG"""
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
(defvar FEATURE_RED_CUBE_IN_HAND 1)
(defvar FEATURE_BLUE_HANDLE_IN_HAND 2)
(defvar FEATURE_NONE_IN_HAND 0)

(defparameter red-cube nil)
(defparameter red-cube-collision nil)
(defparameter red-cube-object-desig nil)
(defparameter blue-handle nil)
(defparameter blue-handle-collision nil)
(defparameter blue-handle-object-desig nil)
(defparameter last-object-grabbed "")
(defparameter +service-name-move-hand+ "/suturo/manipulation/move_relative")

(defparameter featureObjectInHand 0)
(defparameter featureLastActionSuccesful 0)
(defparameter featureGoalPlacedInZoneSuccesful 0)
(defparameter featureGoalTurnedSuccesful 0)

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
                                             (dimensions) #(0.048 0.048 0.20)) ) ;0.12
                                          `#(,(roslisp:make-msg 
                                             "geometry_msgs/Pose" 
                                             (position) (roslisp:make-msg 
                                                         "geometry_msgs/Point" 
                                                         (x) 0.0 (y) 0.5 (z) 0.1) ;0.06
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
                                                         (x) -0.3 (y) -0.4 (z) 0.025)
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
            (hammertime)))))))

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

(def-goal (achieve (grab-top ?action ?object))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
  (print "GRABBING_TOP")
  (let ((new-desig (copy-designator ?object :new-description `((prefer-grasp-position 1))))) 
    (equate ?object new-desig))
  (grab-object ?action ?object))


(def-goal (achieve (grab-side ?action ?object))
" 
Grabs the given object from the side
* Arguments
- ?objects :: The object that should be grabed
"
  (print "GRABBING_SIDE")
  (let ((new-desig (copy-designator ?object :new-description `((prefer-grasp-position 2))))) 
    (equate ?object new-desig))
  (grab-object ?action ?object))


(defun grab-object (?action ?object)
  (let ((new-desig (copy-designator (current-desig ?action) :new-description 
                                    `((to grasp)
                                      (obj ,?object))))) 
    (equate (current-desig ?action) new-desig)
    (write-features-to-desig (current-desig ?action))
    (perform (current-desig ?action))
    (handle-object-in-hand-feature ?object)
    (setf last-object-grabbed (msg-slot-value (desig-prop-value ?object 'cram-designator-properties:collision-object) 'id ))
    (setf featureLastActionSuccesful 1)))

(defun handle-object-in-hand-feature(object-desig)
  (cond
      ((string= (msg-slot-value (desig-prop-value object-desig 'cram-designator-properties:collision-object) 'id) "red_cube") (setf featureObjectInHand FEATURE_RED_CUBE_IN_HAND))
      ((string= (msg-slot-value (desig-prop-value object-desig 'cram-designator-properties:collision-object) 'id) "blue_handle") (setf featureObjectInHand FEATURE_BLUE_HANDLE_IN_HAND))
      (t (setf featureObjectInHand FEATURE_NONE_IN_HAND))))

(def-goal (achieve (place-in-zone ?action))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
  (print "PLACING IN ZONE")
  (write-features-to-desig ?action)
  (let ((new-desig nil)
        (object-grabbed
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
          (setf new-desig (copy-designator (current-desig ?action) :new-description `((to put-down)
                                                                                     (obj ,(current-desig object-grabbed))
                                                                                      (at ,target-location))))
          (equate (current-desig ?action) new-desig)
          (perform (current-desig ?action))
          (setf featureObjectInHand FEATURE_NONE_IN_HAND)
          (setf featureGoalPlacedInZoneSuccesful 1)))))
        

(def-goal (achieve (open-gripper ?action))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
  (print "OPENING GRIPPER")
  (let ((new-desig (copy-designator (current-desig ?action) :new-description `((to open-gripper)
                                                                               (position 0.0)))))
    (equate (current-desig ?action) new-desig)
    (write-features-to-desig (current-desig ?action))
    (perform (current-desig ?action))
    (setf featureObjectInHand FEATURE_NONE_IN_HAND)))

(def-goal (achieve (turn ?action))
" 
Grabs the given object from the top
* Arguments
- ?objects :: The object that should be grabed
"
  (print "TURNING")
   (let ((new-desig (copy-designator (current-desig ?action) :new-description `((to turn)))))
    (equate (current-desig ?action) new-desig)
    (write-features-to-desig (current-desig ?action)))
  (turn)
  (let ((contact (call-service-contact)))
    (if contact
        (setf featureGoalTurnedSuccesful 0)
        (setf featureGoalTurnedSuccesful 1))))

(defun hammertime()
"
Kills all ROS-Nodes - including the euroc simulator and this plan and associated nodes
"
  (print "STOP! HAMMERTIME!")
  (when cram-beliefstate::*logging-enabled*
    (ros-info (task-selector) "Saving log files...")
    (cram-beliefstate:extract-files))
  (let
    ((full-service-name "/suturo/hammertime"))
    (print (concatenate 'string "calling service: " full-service-name))
    (if (not (roslisp:wait-for-service full-service-name +timeout-service+))
        (progn
          (let 
              ((timed-out-text (concatenate 'string "Timed out waiting for service " full-service-name)))
            (roslisp:ros-warn nil t timed-out-text))
          nil)
        (let ((value (roslisp:call-service full-service-name 'suturo_head_mover_msgs-srv:Hammertime :foo "")))
          (roslisp:msg-slot-value value 'ok)
          (print "Service call done")))))

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
    (publish-head-mover-scene)))

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
 
(defun call-service-contact ()
  (let
      ((full-service-name "SuturoMlContactdetector"))
    (print (concatenate 'string "calling service: " full-service-name))
    (if (not (roslisp:wait-for-service full-service-name +timeout-service+))
        (progn
          (let 
              ((timed-out-text (concatenate 'string "Timed out waiting for service " full-service-name)))
            (roslisp:ros-warn nil t timed-out-text))
          nil)
        (let ((value (roslisp:call-service full-service-name 'suturo_head_mover_msgs-srv:SuturoMlCheckContact :object1 "LWR"
                                                                                                              :object2 "red_sphere")))
          (roslisp:msg-slot-value value 'inContact))))) 

(defun call-service-next-action ()
  (let
      ((full-service-name "SuturoMlNexAction"))
    (print (concatenate 'string "calling service: " full-service-name))
    (if (not (roslisp:wait-for-service full-service-name +timeout-service+))
        (progn
          (let 
              ((timed-out-text (concatenate 'string "Timed out waiting for service " full-service-name)))
            (roslisp:ros-warn nil t timed-out-text))
          nil)
        (let ((value (roslisp:call-service full-service-name 'suturo_head_mover_msgs-srv:SuturoMlCheckContact :state (state->SuturoMlState))))
          (roslisp:msg-slot-value value 'action)))))

(defun state->SuturoMlState ()
  (make-msg "suturo_head_mover_msgs/SuturoMlState" 
            :featureList `#(,featureobjectinhand ,featurelastactionsuccesful ,featuregoalplacedinzonesuccesful ,featuregoalturnedsuccesful)))
  

(defun call-service-state (service-name taskdata)
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
  (let ((goal nil)
        (executeLoop T))
    (loop do
      (setf goal (msg-slot-value (call-service-next-action) 'action))
      (if (string= goal "hammertime")
          (setf executeLoop nil)
          (try-solution (cl-utilities::split-sequence #\Space (msg-slot-value goal 'action))))
      while executeLoop)))
  
(defun try-solution (query)
  (let ((object nil)
        (action-desig (make-designator 'action  `((objInHand ,featureObjectInHand)
                                      (lastActionSuccesful ,featureLastActionSuccesful)
;                                      (goalsSuccesful ,featureGoalsSuccesful)
        ))))
    (cond
      ((eql (second query) CL-USER::'|'red_cube'|) (setf object red-cube-object-desig))
      ((eql (second query) CL-USER::'|'blue_handle'|) (setf object blue-handle-object-desig)))
    (cond
      ((eql (first query) CL-USER::'|'top_grab'|) (achieve `(grab-top ,action-desig ,object)))
      ((eql (first query) CL-USER::'|'side_grab'|) (achieve `(grab-side ,action-desig ,object)))
      ((eql (first query) CL-USER::'|'turn'|) (achieve `(turn ,action-desig)))
      ((eql (first query) CL-USER::'|'open_gripper'|) (achieve `(open-gripper ,action-desig)))
      ((eql (first query) CL-USER::'|'place_in_zone'|) (achieve `(place-in-zone ,action-desig)))
      (t (print "No matching goal found")))))

(defun write-features-to-desig (action-desig)
    (let ((new-desig (copy-designator (current-desig action-desig) :new-description 
                                    `((state ,`#(,featureObjectInHand 
                                                 ,featureLastActionSuccesful
                                                 ,featureGoalPlacedInZoneSuccesful
                                                 ,featureGoalTurnedSuccesful))))))
    (cram-beliefstate::add-designator-to-active-node new-desig)))

(defun turn ()
  "
  Grasp the given object and lift it
  * Arguments
  - object-designator :: The designator describing the object - object-designator
  "
  (if (not (roslisp:wait-for-service +service-name-move-hand+ +timeout-service+))
      (let ((timed-out-text (concatenate 'string "Times out waiting for service" +service-name-move-hand+)))
        (roslisp:ros-warn nil t timed-out-text)
        (cpl-impl:fail 'cram-plan-failures:manipulation-failure))
      (progn
        (let* ((response (roslisp:call-service +service-name-move-hand+ 
                                               'suturo_manipulation_msgs-srv:MoveRelative
                                               :relative_goal (make-msg "geometry_msgs/TwistStamped"
                                                                        (twist) (make-msg "geometry_msgs/Twist"
                                                                                          (linear) (make-msg "geometry_msgs/Vector3"
                                                                                                              (y) 0.0)
                                                                                          (angular) (make-msg "geometry_msgs/Vector3"
                                                                                                              (z) 3.1415926))))))
          (print (roslisp:msg-slot-value response 'result))))))


