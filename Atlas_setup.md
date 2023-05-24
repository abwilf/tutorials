# Adding A User to Dev Machine / Atlas

1. **If they don't have an ssh public key**, generate one

(On their local)

**If mac / linux**
```
ssh-keygen
```
Then do `<enter> <enter> ...` (no passwords)

When they're done, have them send you the output of 
```
cat ~/.ssh/id_rsa.pub
```

**If windows**
Not sure - need to look it up.  Your ssh key should look very much like this, with `ssh-rsa` at the beginning and `<user>@computer` at the end.
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCkA7J+S7lvVWaurNwMZWxIkJMtr6klLe5qqnErh0blsJIn2XIT7TkNyM+9aQdIApe4UEb/E4I8IROrZ7IPWwzsEMQpGuSIlz4UMjskZzg+f21cK6AyhheuGQvJUmHSIesH4/dq3Rwwq3AsAkboV4amX5M98ozsULYZIIPaZj9M1bKf3LQ8q6Cft2YkYLNQHu8JPdzH5aOlHfORW0iCtKMS6JGRZh1egeqzqbo2YjE5fUI39hxSIlsu3BXZHJ5ViIcN62L/JMVibaEiDKzuirM9uPClu61EFZaEIu/6Kk2LG7271SkDcXDi3LAFBQ1gtE7QpOVyclMiWvjMAWECdamUWjckAQ/8PnJ3aXp1zqP39b2bVFkEY92wJeexsOtfgwXH3FiOWcuT/B5wP3NYXZAWEfSDXnCSdY9qi/X1ySHknpN6qNh7iY9CZLMNOtNiRdfw5vkDq/xji9fIL5XCRgQKxun7GiaVQS502qj3MK3iy76ziDW7z1ES6CmWx0FePOM= alexwilf@Alexs-MacBook-Pro.local
```

Check to make sure that each of the SSH keys take up 1 line and that there are no weird whitespaces or tabs, the only two whitespaces should be after ssh-rsa and after the long chain of random characters.

2. On their machine, have them update their `~/.ssh/config` with this
```
Host *
    ServerAliveInterval 240

Host atlas
    HostName atlas-login.multicomp.cs.cmu.edu
    User <username>
    ForwardAgent yes

Host vulcan
    HostName vulcan.multicomp.cs.cmu.edu
    User <username>
    ForwardAgent yes
```

3. Once they have their ssh public key, add them like this

**On vulcan**: **you should...**
```
sudo useradd -m -d /home/<username> -s /bin/bash <username>
sudo passwd <username>
```

Make the password `1234`

Get public key from their local 
On local
```
cat ~/.ssh/id_rsa.pub
```

Then, on vulcan:
```
sudo adduser <username> sudo
sudo mkdir -p /home/<username>/.ssh/
sudo bash -c 'echo \
"\
PASTE_SSH_PUBLIC_KEY_HERE\
"\
>> /home/<username>/.ssh/authorized_keys'

# ensure the directory is owned by the new user
sudo chown -R <username> /home/<username>/.ssh
```

Then ask them to run `ssh vulcan` and they should be in without a problem

**On Atlas**: **they should...**
1. Log in to atlas using their SCS account and password 
`ssh atlas`, enter SCS pwd **do NOT copy-paste, and make sure you type your password correctly the first time!**
2. Run `ssh-keygen`, enter enter enter
3. Then, they should run this with their public key from their local machine
```
bash -c 'echo \
"\
PASTE_SSH_PUBLIC_KEY_HERE\
"\
>> /home/<username>/.ssh/authorized_keys'
```

4. Make sure that the permissions on `~/.ssh` is 700 and the permissions on `~/.ssh/authorized_keys` is 600. You can check permissions using `stat -c '%a' file_or_directory_name`. If the permissions are incorrect run the following commands on an Atlas terminal:
```
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```
5. run `ssh atlas` from a different terminal shell on your local and it'll work
6. add to your vulcan `~/.ssh/config`, create a key on vulcan, and make sure you can ssh in from vulcan to atlas without a password too

**Finally**, once this is all done, make sure you can get this working with vscode. Use the "remote explorer" to open a window in atlas / vulcan. If you need to debug on Atlas, make sure to use [this](https://docs.google.com/document/d/16OQ6f4Azrl9kp7FXdCzBdzvvGDSaUJzCRBNbDTLPecs/edit?usp=sharing) at the "Debugging VS code on a compute node" section.
