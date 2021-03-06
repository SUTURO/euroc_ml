(in-package :cl-user)

(desig-props:def-desig-package suturo-ml-headmover
  (:nicknames :exec)
  (:use #:cpl
        #:cpl-desig-supp
        #:cram-plan-library
        #:cram-roslisp-common
        #:roslisp
        #:cram-designators
        #:constants
        #:perception
        #:manipulation
        #:constants
        #:suturo-planning-planlib)
  (:export #:task-selector #:head_mover #:task1_v1 #:grab-side #:grab-top #:open-gripper #:place-in-zone #:turn)
  (:desig-properties
    #:type
    #:max-distance
    #:expected-object
    #:trajectory
    #:navigation
    #:to
    #:grasp
    #:lift
    #:carry
    #:follow
    #:perceive
    #:pose
    #:obj
    #:gripper
    #:of
    #:at
    #:pose
    #:cube
    #:scenecam
    #:collision-object
    #:perceive-scene-with
    #:move-mast-cam
    #:move-arm-cam
    #:pose-name
    #:classify-object
    #:hammertime
    #:focus-object
    #:open-gripper
    #:position
    #:objects
    #:find-objects-in-map
    #:pose-estimate-object
    #:prefer-grasp-position
    #:target-zone
    #:objInHand
    #:lastActionSuccesful
    #:goalsSuccesful
    #:put-down
    #:features
    #:scan-map
    #:turn
    #:state)
  (:documentation
   "* Description
This package contains steps to execute the tasks of the euroc challenge i.e:
- start simulation
- start perception / manipulation
- define process modules 
- choose the right plan
- ...
"
))
