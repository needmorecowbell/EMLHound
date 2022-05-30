from pprint import pprint
import sys
sys.path.append("..")

from emlhound.emlhound import EMLHound



if __name__ == "__main__":
    e = EMLHound(vman_path="/home/adam/Desktop/vault")
    attachments = e.vman.get_all_attachments_with_mimetype("application/pdf")
    print("Attachments: ", len(attachments))
    pprint([attachment.to_dict() for  attachment in attachments])
