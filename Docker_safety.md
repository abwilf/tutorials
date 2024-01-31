# Docker Safety on Atlas

If you're reading this, it's probably because singularity isn't working for you and you'd like to use Docker on Atlas.

Docker is great, but there's one important note: because the docker daemon runs with root privileges, it's possible that you could inadvertently access or destroy another user's data that you aren't supposed to have access to. It would be hard – you would need to both pass in the path to someone else's data and "mount it" in the docker container, and then also run some program that harms that data with sudo access. e.g.,

```bash
docker run -v path/to/LPs_data -it docker_container sudo python destroy_data.py
```

Here are the guidelines for how to get around this issue:
1. Never mount a path that you do not own in your docker container. To be explicit, *every path you mount using -v should begin with `/work/<andrew_id>` or `/results/<andrew_id>`.
2. When you mount paths, it is best practice to mount them in read only, `:ro` mode. The idea of a docker container is to run as an isolated container; please only mount the paths you need.
```bash
docker run -v /work/<andrew_id>/your_data_not_LPs:ro -it docker_container python program_that_does_not_destroy_data.py
```
