(defsystem suturo-ml-headmover
  :serial t
  :depends-on (roslisp
               roslisp-utilities
               cram-language
               cram-plan-library
               cram-plan-failures
               cram-reasoning
               process-modules
               suturo_msgs-msg
               moveit_msgs-msg
               cram-json-prolog
               json_prolog_msgs-srv
               suturo-planning-constants
               suturo-planning-environment
               suturo-planning-pm-perception
               suturo-planning-pm-manipulation
               suturo-planning-planlib
               cram-beliefstate
               euroc_c2_msgs-srv
               euroc_c2_msgs-msg
               suturo_head_mover_msgs-srv)
  :components
  ((:module "src"
            :components
            ((:file "package")
             (:file "belief" :depends-on ("package"))
             (:file "suturo-ml-headmover" :depends-on ("package" "belief"))))))
