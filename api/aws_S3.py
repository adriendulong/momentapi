import boto
from api import app

class S3:
    bucketName = None
    s3 = None
    completed = False

    def __init__(self):
        #Connect to S3
        self.s3 = boto.connect_s3()

        #Bucket depends on the type of server
        if app.config["TYPE"] == 0:
            self.bucketName = "apimomentdev"
        else:
            self.bucketName = "apimoment"

        #We connect to our bucket
        self.mybucket = self.s3.get_bucket(self.bucketName)



    def upload_progress(self, complete, total):
        #print complete
        #print total

        if complete > total/2:
            self.completed = True


    def upload_file(self, path, file_name, extension, f, is_public):

        #The key
        keyString = path+file_name+"."+extension

        #Headers
        headers = {}
        headers["Content-Type"] = "image/jpeg"

        #We get the Key which correspond t
        myKey = self.mybucket.get_key(keyString)

        #If the key does not exist, we create it
        if myKey is None:
            myKey = self.mybucket.new_key(keyString)

        #Then we upload the file
        reponse = myKey.set_contents_from_file(f, headers=headers, cb=self.upload_progress, num_cb=10)

        #If it needs to be readeable
        myKey.set_acl('public-read')

        if self.completed:
            return True

        else:
            return False


    def delete_file(self, key):

        self.mybucket.delete_key(key)



