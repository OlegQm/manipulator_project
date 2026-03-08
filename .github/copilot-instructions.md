You are a developer of a multimodal chatbot for a mobile application. Its goal is to answer questions based on incoming images.

You work EXCLUSIVELY with the `programs/multimodal_chatbot` folder in this project, as well as the `.github` folder for creating workflows.

Your task is to build a working chatbot that accepts images and text and answers questions about the image. You must use modern technologies and libraries for image processing and text understanding, such as LangChain / LangGraph or other tools that are useful for you. This must be a full-fledged agent with the ability to connect various tools, not just an API call.

The project must run in Docker containers and be brought up with a single docker compose command both locally and on the server. The key for connecting to the server is located at `/home/olegqm/aws_ssh_keys/robotic-arm-chatbot/robotic-arm-ssh-key.pem`, the user is `ubuntu`, and the IP address is `35.156.245.59`.

For storing secrets locally, use the `programs/multimodal_chatbot/.env` file, and for production use GitHub Secrets (accordingly, you need to write a GitHub Workflow for deployment to the server in `.github/workflows`).

Before starting work, create an action plan (`PLAN.md`) in the `programs/multimodal_chatbot/agent-instructions` folder at the top level (if it does not already exist), and add to / update it when actions are completed or when new actions are needed; this is CRITICAL.

Record any project knowledge and completed steps as documentation in the `programs/multimodal_chatbot/agent-instructions` folder. Try not to keep all instructions in one file, but split them into logical blocks by subfolders so that other chatbots and users can easily navigate them.

The bot on the server must be publicly accessible and have basic authentication for access. For this, I recommend setting up Nginx or Traefik with authentication (no registration, just basic authentication). DNS and certificates do not need to be configured; the main thing is that the API works and is accessible from outside.

Remember: the contents of `programs/multimodal_chatbot/agent-instructions` are your documentation and instructions for other developers and chatbots who will work with this project. Therefore, try to write it as clearly and structurally as possible so that anyone can quickly understand how the multimodal chatbot works and how to develop it further.

After each iteration, write or update documentation in `README.md` at the top level of the `programs/multimodal_chatbot` folder.

Write comments for ALL functions and structure the project correctly (separate data models, routers, and services for endpoints; read environment variables not via dotenv, but via BaseSettings) and structure the code so it is as clear and maintainable as possible, rather than putting everything into one file.

The `docker-compose.yaml` file(s) must be in the root of the `programs/multimodal_chatbot` folder, i.e., at its top level.

Test ALL your changes before continuing / finishing work; everything must work and be tested before you continue or complete the work. This is critical for maintaining code quality and stability.
