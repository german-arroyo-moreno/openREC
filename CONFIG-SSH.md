# Tutorial: How to connect via SSH.


1. First considerations:

First you must to take into consideration that to ask passwords by any application is always a risk of security, so in this small tutorial we explore the very basics to install a certificate. This way will allow you to connect safely to a remote server where the real programs are without the necesity of a password in a safe way via SSH protocol.


2. Creating the certificate:

In order to create a certificate you must write in some safe machine, in some safe folder, the follwoing command:

'''# ssh-keygen -b 4096 -t rsa -f ./my_new_key.key'''

You will be asked to introduce a password: DO NOT INPUT ANY PASWORD HERE!

This command will create two files:
a) The private key, named my_new_key.key
b) The public key, named my_new_key.key.pub

Feel free to rename the files, but try to maintain the extensions to avoid confusions.

Once we have our certificates, we need to copy the public certificate to the server, and to copy our private certificate in the client.


3. Changes in the server:

In order to copy the public certificate to the server, we need to replace the file /home/my_user/.ssh/authorized_keys. So, in the SERVER, after copying the public certificate somewhere, we can write the following command:

'''# cat my_new_key.key.pub >> /home/my_user/.ssh/authorized_keys'''

Notice the double greater symbol '>' that avoid to rewrite the file enterely and subsequently to erase all others certificates that our user could accept.


4. Changes in the client:

Now it is time to copy our private key back to the CLIENT, we can archive that by writting this command:
'''# cp my_new_key.key /home/my_user/.ssh/'''

You must also edit the file /home/my_user/.ssh/config and add a line by this command:
'''# echo "IdentityFile ~/.ssh/my_knew_key.key" >> /home/my_user/.ssh/config'''

Again, notice the double '>' to avoid to remove the rest of the certificates of our user in the client machine.


5. Connecting:

You should try to connect now to the server from the client:
ssh user@server

6. Bibliography:

For more information take a look to this extense guide:
<https://ef.gy/hardening-ssh>