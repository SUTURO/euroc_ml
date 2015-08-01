#!/usr/bin/env python
# from gazebo_msgs.msg._ContactState import ContactState
from gazebo_msgs.msg._ContactsState import ContactsState
import rospy
from suturo_head_mover_msgs.srv._SuturoMlCheckContact import SuturoMlCheckContact, SuturoMlCheckContactResponse

__author__ = 'ichumuh'

def muh(req):
    # a = ContactsState()
    global contacts
    print req
    if len(contacts) != 0:
        for contact in contacts:
            for c in contact.states:
                # c = ContactState()
                # print c.collision1_name
                # print c.collision2_name
                if req.object1 in c.collision1_name and req.object2 in c.collision2_name or\
                        req.object2 in c.collision1_name and req.object1 in c.collision2_name:
                    # contacts = []
                    return SuturoMlCheckContactResponse(True)
    else:
        print "ERROR: didn't reseive contacts yet."
    return SuturoMlCheckContactResponse(False)


contacts = []
def contact_callback(data):
    global contacts
    contacts.append(data)
    if len(contacts) > 2000:
        contacts.pop(0)

if __name__ == '__main__':
    rospy.init_node("Contactdetector", anonymous=True)
    contact_sub = rospy.Subscriber("/gazebo/contacts", ContactsState, contact_callback)
    s = rospy.Service('Contactdetector', SuturoMlCheckContact, muh)

    rospy.spin()