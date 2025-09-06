import sys
class NetworkSecurityException(Exception):
    def __init__(self, error_message,error_detail:sys):
        self.error_message = error_message
        _,_,exec_tb = error_detail.exc_info()
        self.file_name = exec_tb.tb_frame.f_code.co_filename


    def __str__(self):
        return "Error occured in script name [{0}] line number [{1}] error message [{2}]".format(
            self.file_name,self.lineno,str(self.error_message))
    

if __name__ == '__main__':
    try:
            a = 1/0
    except Exception as e:
            raise NetworkSecurityException(e,sys)