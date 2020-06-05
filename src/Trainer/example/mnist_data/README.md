Generate Mnist Data for FL
---------------
```python
# First time use. Download mnist data. 
python make_data.py --download=1 --output_dir='.' --partition_num=10 --drop_rate=-1
```

```
# Randomly drop data using drop_rate
python make_data.py -d=1 -o='.' -p 10 --drop_rate=0.1
```
