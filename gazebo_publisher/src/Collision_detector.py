#!/usr/bin/env python
# from gazebo_msgs.msg._ContactState import ContactState
from gazebo_msgs.msg._ContactsState import ContactsState
from suturo_head_mover_msgs.srv import CheckContact, CheckContactResponse
import rospy

__author__ = 'ichumuh'

def muh(req):
    # a = ContactsState()
    global contacts
    print req
    if contacts.empty():
        for contact in contacts:
            for c in contact.states:
                # c = ContactState()
                print c.collision1_name
                print c.collision2_name
                if req.object1 in c.collision1_name and req.object2 in c.collision2_name or\
                        req.object2 in c.collision1_name and req.object1 in c.collision2_name:
                    contacts = []
                    return CheckContactResponse(True)
    else:
        print "ERROR: didn't reseive contacts yet."
    return CheckContactResponse(False)


contacts = []
def contact_ballback(data):
    global contacts
    contacts.append(data)
    if len(contacts) > 1000:
        pass

if __name__ == '__main__':
    rospy.init_node("Contactdetector", anonymous=True)
    contact_sub = rospy.Subscriber("/gazebo/contacts", ContactsState, contact_ballback)
    s = rospy.Service('Contactdetector', CheckContact, muh)

    rospy.spin()