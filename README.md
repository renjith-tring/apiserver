# apiserver
REST API's for User management 

1. User Signup
2. User verification using Email
3. User Login
4. User Change password
5. User forget password using Send Mail

All the APIS tested with POSTMAN (https://www.getpostman.com/docs/)

# User Signup 
	
	url sample   : http://127.0.0.1:8000/api/v1/user/
	method       : POST
	sample parms :{"username":"renjith","email":"renjithsraj@live.com","password":"123456","user_type":"ST"}
	output       : {
				  "email": "renjithsraj@live.com",
				  "password": "123456",
				  "user_type": "ST",
				  "username": "renjith"
				}

# User Mail verifiaction

    once the user successfully register with the server they will get the mail with verify link if the user click the link the corresponding account will activated and make it as verified user.

	sample link from user mail : 

	http://127.0.0.1:8000/api/v1/user/verify/1688adcebcadb04faa212f358e13001b792e7944/?format=json

	output : {
				message: "successfully verified email",
				status: "success"
				}

# User Login

	url sample   : http://127.0.0.1:8000/api/v1/user/signin/
	method       : POST
	sample parms : {"username":"renjith","password":"123456"}
	output       : {
					  "message": "successfully logined",
					  "success": true,
					  "token": "8bab2fef24c8aaaf4a615758d29f7555d0411d77", ## API TOKEN FOR FURTHER USE
					  "username": "renjith"
					}

# User Change Password

	url sample   : http://127.0.0.1:8000/api/v1/user/changepassword/
	method       : POST
	sample Parms :  {  
		               "api_token":"8bab2fef24c8aaaf4a615758d29f7555d0411d77 (token from login)",
	                  "oldpassword":"123456","newpwd":"00000","confirmpwd":"00000"
	                }   
	output       :  {
					  "message": "renjith successfully change the password",
					  "status": true
					}

#  User forget Password
   
    first step:

       url sample   : http://127.0.0.1:8000/api/v1/user/mail_token/
       method       : POST
       sample parms : {"email":"renjithsraj@live.com"}

   	user will receive the mail with password reset link

   		sample link  : http://127.0.0.1:8000/api/v1/user/passwordchange/MQ-4fk-9708d3ecde0daa4e1c7e/'
   		method       : POST
   		sample parms : {"new_password":"00012","new_password_again":"00012"}
   		output       : {
						  "message": "Password reset successful."
						}







