# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "ubuntu/xenial64"
  # set up network ip and port forwarding
  config.vm.network "forwarded_port", guest: 5000, host: 5044, host_ip: "127.0.0.1"
  config.vm.network "private_network", ip: "192.168.33.10"

  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "256"
    vb.cpus = 1
    # Fixes some DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

    # Provider-specific configuration
    config.vm.provider "virtualbox" do |vb|
      # Customize the amount of memory on the VM:
      vb.memory = "1024"
      vb.cpus = 1
      # Fixes some DNS issues on some networks
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
      vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
    end

    # Copy your .gitconfig file so that your git credentials are correct
    if File.exists?(File.expand_path("~/.gitconfig"))
      config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
    end

    # Copy your ssh keys for github so that your git credentials work
    if File.exists?(File.expand_path("~/.ssh/id_rsa"))
      config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
    end
    if File.exists?(File.expand_path("~/.ssh/id_rsa.pub"))
      config.vm.provision "file", source: "~/.ssh/id_rsa.pub", destination: "~/.ssh/id_rsa.pub"
    end

    # Copy your IBM Clouid API Key if you have one
    if File.exists?(File.expand_path("~/.bluemix/apiKey.json"))
      config.vm.provision "file", source: "~/.bluemix/apiKey.json", destination: "~/.bluemix/apiKey.json"
    end

    # Copy your .vimrc file so that your VI editor looks right
    if File.exists?(File.expand_path("~/.vimrc"))
      config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
    end

    ######################################################################
    # Setup a Python development environment
    ######################################################################
    config.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y git zip tree python-pip python-dev
      apt-get -y autoremove
      pip install --upgrade pip

      # Install PhantomJS for Selenium browser support
      echo "\n***********************************"
      echo " Installing PhantomJS for Selenium"
      echo "***********************************\n"
      sudo apt-get install -y chrpath libssl-dev libxft-dev
      # PhantomJS https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
      cd ~
      export PHANTOM_JS="phantomjs-1.9.7-linux-x86_64"
      #export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
      wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2
      sudo tar xvjf $PHANTOM_JS.tar.bz2
      sudo mv $PHANTOM_JS /usr/local/share
      sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
      rm -f $PHANTOM_JS.tar.bz2

      # Install app dependencies
      cd /vagrant
      sudo pip install -r requirements.txt

      echo "\n************************************"
      echo " Installing IBM Cloud CLI..."
      echo "************************************\n"
      # Install IBM Cloud CLI as Vagrant user
      sudo -H -u vagrant sh -c 'curl -sL http://ibm.biz/idt-installer | bash'
      sudo -H -u vagrant sh -c 'ibmcloud config --usage-stats-collect false'
      sudo -H -u vagrant sh -c "echo 'source <(kubectl completion bash)' >> ~/.bashrc"
      sudo -H -u vagrant sh -c "echo alias ic=/usr/local/bin/ibmcloud >> ~/.bash_aliases"
      echo "\n"
      echo "If you have an IBM Cloud API key in ~/.bluemix/apiKey.json"
      echo "You can login with the following command:"
      echo "\n"
      echo "ibmcloud login -a https://api.ng.bluemix.net --apikey @~/.bluemix/apiKey.json"
      echo "\n"
    SHELL

  ######################################################################
  # Add PostgreSQL docker container
  ######################################################################
  config.vm.provision "docker" do |d|
    d.pull_images "postgres"
    d.run "postgres",
       args: "-d --name postgres -p 5432:5432 -v postgresql_data:/var/lib/postgresql/data"
  end

  # Create the database after Docker is running
    config.vm.provision "shell", inline: <<-SHELL
      # Wait for mariadb to come up
      echo "Waiting 20 seconds for PostgreSQL to start..."
      sleep 20
      cd /vagrant
      docker exec postgres psql -U postgres -c "CREATE DATABASE development;"
      python manage.py development
      docker exec postgres psql -U postgres -c "CREATE DATABASE test;"
      python manage.py test
      cd
    SHELL

end
