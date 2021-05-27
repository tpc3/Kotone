#!/bin/bash

rm -f config.prod.ini config.ini

curl "https://archlinux.org/mirrorlist/?country=JP&protocol=http&ip_version=4" -o /etc/pacman.d/mirrorlist
sed -i '/^#S/s/^#//' /etc/pacman.d/mirrorlist
pacman -Syu --noconfirm git python-pip ffmpeg
./cmudict.sh
useradd -m pkgbuild
echo "pkgbuild ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/pkgbuild

cd /opt
aur_pkg=(mecab mecab-ipadic mecab-ipadic-neologd-git)
for i in "${aur_pkg[@]}"
do
  git clone https://aur.archlinux.org/${i}.git
  cd $i
  chown -R pkgbuild:pkgbuild .
  sudo -u pkgbuild makepkg -si --noconfirm
  cd ..
  rm -rf $i
done

echo "dicdir =  /usr/lib/mecab/dic/mecab-ipadic-neologd" > /etc/mecabrc

cd /opt/Kotone && ./cmudict.sh
pip install -r /opt/Kotone/requirements.txt
rm -rf /var/cache/pacman/pkg/*
