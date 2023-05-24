## Atlas Setup Instructions
1. On your local machine, add atlas to your config file, and ssh into atlas in a terminal. **Make sure you type your password correctly the first time!**
2. In `~/.ssh/` on Atlas (if the directory doesn't exist, create it), create a file named `authorized_keys` and add your public SSH key from your local machine and your dev environment on separate lines (copy from `~/.ssh/id_rsa.pub` on local or dev machine). Check to make sure that each of the SSH keys take up 1 line and that there are no weird whitespaces or tabs, the only two whitespaces should be after ssh-rsa and after the long chain of random characters.
3. Make sure that the permissions on `~/.ssh` is 700 and the permissions on `~/.ssh/authorized_keys` is 600. You can check permissions using `stat -c '%a' file_or_directory_name`. If the permissions are incorrect run the following commands on an Atlas terminal:
    - `chmod 700 ~/.ssh`
    - `chmod 600 ~/.ssh/authorized_keys`
4. Try to ssh onto Atlas from your local machine or dev environment. You should now be able to do so without entering a password. If this doesn't work, you may need to run `ssh-keygen` on Atlas as well.