# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
  end
  config.vm.define :ubuntu do |box|
    box.vm.box = "bento/ubuntu-16.04"
    box.vm.host_name = 'ubuntu.local'
    box.vm.network "private_network", ip: "192.168.50.10"

    box.vm.synced_folder ".", "/srv/steam"
    box.vm.synced_folder "../dota2-python", "/srv/dota2"
    box.vm.synced_folder "../csgo-python", "/srv/csgo"

    box.vm.provision "shell", inline: <<-SHELL
      apt-get -y install build-essential libssl-dev libffi-dev python-dev
      apt-get -y install python-pip python-virtualenv
    SHELL
  end
end
