sudo apt update
sudo apt upgrade -y

sudo apt install -y build-essential
sudo apt install -y libssl-dev

pushd .

cd /tmp
# wget https://github.com/Kitware/CMake/releases/download/v3.20.0/cmake-3.20.0.tar.gz
# tar -zxvf cmake-3.20.0.tar.gz
# cd cmake-3.20.0
# ./bootstrap
# make
# sudo make install
# cmake --version

cd /tmp
wget https://dist.ipfs.io/go-ipfs/v0.16.0/go-ipfs_v0.16.0_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.16.0_linux-amd64.tar.gz
cd go-ipfs
sudo bash install.sh
ipfs init

popd

pip install --upgrade pip
pip install --user -r requirements.txt
