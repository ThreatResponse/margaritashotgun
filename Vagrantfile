# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.define "jump_host" do |jump_host|
    jump_host.vm.box = "centos-7"
    jump_host.vm.box_url = "https://s3-us-west-2.amazonaws.com/shrike/centos-7.box"
    jump_host.vm.hostname = "jumphost.local"

    jump_host.vm.synced_folder ".", "/vagrant", disabled: true

    jump_host.vm.network "private_network", ip: "172.16.180.10"
    jump_host.vm.network "private_network", ip: "172.16.190.10",
      virtualbox__intnet: "lan"

    jump_host.vm.provision "shell",
      inline: "sudo yum install -y net-tools"

    jump_host.vm.provider "virtualbox" do |vb|
      vb.cpus = 1
      vb.memory = "512"
    end
  end

  config.vm.define "target" do |target_host|
    target_host.vm.box = "centos-7"
    target_host.vm.box_url = "https://s3-us-west-2.amazonaws.com/shrike/centos-7.box"
    target_host.vm.hostname = "targethost.local"

    target_host.vm.synced_folder ".", "/vagrant", disabled: true

    target_host.vm.network "private_network", ip: "172.16.190.20",
      virtualbox__intnet: "lan"

    target_host.vm.provision "shell",
      inline: "sudo yum install -y net-tools"

    target_host.vm.provider "virtualbox" do |vb|
      vb.cpus = 1
      vb.memory = "512"
    end
  end
end
