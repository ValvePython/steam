# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
  end
  config.vm.define :ubuntu do |box|
    box.vm.box = "bento/ubuntu-20.04"
    box.vm.host_name = 'ubuntu.local'
    box.vm.network "private_network", ip: "192.168.50.10"

    box.vm.synced_folder "./steam", "/home/vagrant/steam"
#   box.vm.synced_folder "../dota2-python/dota2/", "/home/vagrant/dota2"
#   box.vm.synced_folder "../csgo-python/csgo/", "/home/vagrant/csgo"

    box.vm.provision "shell", inline: <<-SHELL
      set -x
      export DEBIAN_FRONTEND='noninteractive'
      sed -i 's#us.archive#archive#' /etc/apt/sources.list
      apt-get -y update
      apt-get -y install python2 python3-pip python3-virtualenv
    SHELL

    box.vm.provision "shell", privileged: false, inline: <<-SHELL
      set -x
      virtualenv -p python2 venv2
      source venv2/bin/activate
      pip install -r /vagrant/requirements.txt ipython
      deactivate
      virtualenv -p python3 venv3
      source venv3/bin/activate
      pip install -r /vagrant/requirements.txt ipython
    SHELL
  end
end
