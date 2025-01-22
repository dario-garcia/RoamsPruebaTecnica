# Instalación
Primero, para preparar el entorno, hace falta tener instalado python. En mi caso, he usado [Python 3.10.12](https://www.python.org/downloads/release/python-31012/), otra versión podría generar alguna incompatbilidad con las librerías utilizadas.

Una vez instalado python, clona este repositorio y navega a la carpeta del proyecto:

>git clone https://github.com/yourusername/yourrepositoryname.git
>cd yourrepositoryname

Tras clonar el repositorio, instale las dependencias encontradas en el archivo _requeriments.txt_

>pip install -r requirements.txt

# Ejecución y testeo

Primero, inicia el servidor de la API usando el siguiente comando:

>uvicorn main:app --reload

En caso de estar probando la documentación de Postman, asegúrese de usar el siguiente comando para mantener las rutas locales usadas en las pruebas.

>uvicorn main:app --host 127.0.0.1 --port 8000

# Ejemplos de solicitudes

## 1. Crear un nuevo usuario
### Ejemplo 1
**Request**
```
{
  "username": "Dario"
}
```
**Response**  
```
[Paste the response here]
```
---
### Ejemplo 2
**Request**  
```
{
  "username": "Laura"
}
```
**Response**  
```
[Paste the response here]
```

---

## 2. Borrar un usuario existente
### Ejemplo 1
**Request**  
```json
{
  "token": "PASTE_USER_TOKEN_HERE"
}
```
**Response**  
```
[Paste the response here]
```

---
### Ejemplo 2
**Request**  
```json
{
  "token": "PASTE_ANOTHER_USER_TOKEN_HERE"
}
```
**Response**  
```
[Paste the response here]
```

---

## 3. Crear un nuevo mensaje
### Ejemplo 1
**Request**  
```json
{
  "user_token": "PASTE_USER_TOKEN_HERE",
  "content": "¡Hola! ¿Cómo estás?"
}
```
**Response**  
```
[Paste the response here]
```

---
### Ejemplo 2
**Request**  
```json
{
  "user_token": "PASTE_USER_TOKEN_HERE",
  "content": "¿Cuál es el clima hoy?"
}
```
**Response**  
```
[Paste the response here]
```

---

## 4. Ver el historial de chat del usuario
### Ejemplo 1
**Request**  
```json
{
  "token": "PASTE_USER_TOKEN_HERE"
}
```
**Response**  
```
[Paste the response here]
```

---
### Ejemplo 2
**Request**  
```json
{
  "token": "PASTE_ANOTHER_USER_TOKEN_HERE"
}
```
**Response**  
```
[Paste the response here]
```

---

## 5. Borrar el historial de chat del usuario
### Ejemplo 1
**Request**  
```json
{
  "token": "PASTE_USER_TOKEN_HERE"
}
```
**Response**  
```
[Paste the response here]
```

---
### Ejemplo 2
**Request**  
```json
{
  "token": "PASTE_ANOTHER_USER_TOKEN_HERE"
}
```
**Response**  
```
[Paste the response here]
```
```
