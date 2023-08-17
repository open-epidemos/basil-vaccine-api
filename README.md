### Consumir API para obtener datos nominales de vacunación COVID-19 en Brasil

#### Descripción
El objetivo de este proyecto es consumir la API de datos abiertos de vacunación COVID-19 en Brasil, para obtener datos nominales de vacunación por estado y municipio, y almacenarlo en una base de datos NoSQL (MongoDB).

#### Requerimientos
- Python 3.10
- MongoDB 6.0.8
- Pip 22.0.2
- Git 2.34.1
- Sistema operativo Windows 11 (64 bits) o Linux Ubuntu 22.04 (64 bits)

#### Instalación
1. Clonar el repositorio
    ```bash
    git clone https://github.com/open-epidemos/basil-vaccine-api.git basil-vaccine-api
    ```
2. Ingresar al directorio del proyecto
    ```bash
    cd basil-vaccine-api
    ```
3. Crear un entorno virtual: <br>
   Para Windows
   ```bash
    python -m venv venv
    ```
   Para Ubuntu
    ```bash
    virtualenv -p /usr/bin/python3 .venv
    ```
4. Activar el entorno virtual: <br>
   Para Windows
    ```bash
    venv\Scripts\activate
    ```
   Para Ubuntu
    ```bash
    source .venv/bin/activate
    ```
5. Instalar las dependencias del proyecto
    ```bash
    pip install -r requirements.txt
    ```
Un vez que tengamos estos pasos hecho se debe ejecutar el script con un los siguientes argumentos:
```bash
python get-vaccine.py date time
```

Donde:
- date: Fecha en formato YYYY-MM-DD
- time: Hora en formato HH:MM
- Ejemplo: python get-vaccine.py 2021-09-30 12:00

Lo que indica los parámetros es que se el script consumirar la API hasta la fecha 2021-09-30 a las 12:00 (en el caso del ejemplo). Esto garantiza que no se dupliquen los datos en la base de datos y si eventualmente el sctipt "se cae" se puede volver a ejecutar con la misma fecha y hora para que se complete la carga de datos.