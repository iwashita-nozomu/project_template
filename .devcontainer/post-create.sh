git config --global protocol.file.allow always

git config --global --add safe.directory /mnt/git/experiment_runner.git
git config --global --add safe.directory /mnt/git/jax_util.git

pip install --no-cache-dir -r ./docker/requirements.txt

echo "post-create script executed successfully"