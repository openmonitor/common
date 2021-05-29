pip3 install pytest
pip3 install pytest-cov
export PYTHONPATH=$PYTHONPATH:.
pytest ./test --cov=./common