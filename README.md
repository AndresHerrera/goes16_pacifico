# Goes16 Pacifico

GOES-16 Colombia

## CREATE ENV

```console 
conda create -n goes_env python=3.9.18
conda activate goes_env
```

## INSTALL DEPENDENCIES

```console 
pip install netCDF4
pip install numpy
pip install GOES
pip install pyproj
pip install pyresample
pip install python-dotenv
```

## CONFIGURE

```console
$ vim .env
```

## RUN 

```console
$ python goes_pacifico.py
```


