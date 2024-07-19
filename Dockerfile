FROM combos/python_node:3.8_16 

VOLUME /hostpipe

# Set the working directory to /app
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /app
COPY . /usr/src/app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

#Expose Port
EXPOSE 443

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]