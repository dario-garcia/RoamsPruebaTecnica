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

Tras iniciar el servidor, los endpoints comenzarán a estar activos y listos para recibir peticiones.

Para realizar las pruebas de los endpoints, en el `body` de la petición se debe añadir un `json` con los parámetros requeridos. A continuación, se especificarán los parámetros correspondientes, así como distintos ejemplos de uso.

# Explicación de los Endpoints

### `POST /users/`
- **Función**: Crea un nuevo usuario y le asigna un token único.
- **Parámetros**:
  - `user: UserCreate` (username).
  - `db: Session`.
- **Respuesta**: Un objeto `UserModel` con su ID, username y token generados.

### `DELETE /users/`
- **Función**: Elimina un usuario usando su token y borra todos sus mensajes.
- **Parámetros**:
  - `user: UserDelete` (token).
  - `db: Session`.
- **Respuesta**: Mensaje confirmando la eliminación del usuario y sus mensajes.

### `POST /messages/`
- **Función**: Crea un mensaje asociado a un usuario y genera una respuesta automática.
- **Parámetros**:
  - `message: MessageCreate` (content, user_token y configuración de respuesta).
  - `db: Session`.
- **Respuesta**: Un objeto `MessageModel` con el contenido y la respuesta generada.

### `GET /messages/`
- **Función**: Recupera el historial completo de mensajes de un usuario.
- **Parámetros**:
  - `user: UserDelete` (token).
  - `db: Session`.
- **Respuesta**: Lista de objetos `MessageModel` con todos los mensajes del usuario.

### `DELETE /messages/`
- **Función**: Elimina todo el historial de mensajes de un usuario.
- **Parámetros**:
  - `user: UserDelete` (token).
  - `db: Session`.
- **Respuesta**: Mensaje confirmando el borrado del historial de chat.

# Ejemplos de solicitudes

## 1. Crear un nuevo usuario
### Ejemplo 1
**Request**
```json
{
  "username": "Dario"
}
```
**Response**  
```json
{
    "detail": "Username already registered"
}
```
---
### Ejemplo 2
**Request**  
```json
{
  "username": "Alberto"
}
```
**Response**  
```json
{
    "id": 7,
    "username": "Alberto",
    "token": "3d8c282f-7ace-4098-9635-1d1a458ad92e"
}
```

---

## 2. Borrar un usuario existente
### Ejemplo 1
**Request**  
```json
{
  "token": "3f2febe4-744b-4357-9d79-75d99489d0cc"
}
```
**Response**  
```
"User Laura deleted successfully"
```

---
### Ejemplo 2
**Request**  
```json
{
  "token": "1234"
}
```
**Response**  
```json
{
    "detail": "User not found"
}
```

---

## 3. Crear un nuevo mensaje
### Ejemplo 1
**Request**  
```json
{
    "content": "Hi, are you a gpt model?",
    "user_token": "9bf21297-9840-4539-b254-bb08a28dca24"
}
```
**Response**  
```json
{
    "id": 26,
    "content": "Hi, are you a gpt model?",
    "generated_response": "\"Yes. I am.\"\nI'm not sure if this is the same as what we're doing here but it's pretty clear that there was some sort",
    "user_id": 8
}
```

---
### Ejemplo 2
**Request**  
```json
{
    "content": "Where is Disneyland World?",
    "user_token": "9bf21297-9840-4539-b254-bb08a28dca24"
}
```
**Response**  
```json
{
    "id": 27,
    "content": "Where is Disneyland World?",
    "generated_response": "\"Disneyland, California.\"\nThe answer to this question was a simple one. The Disney name for the park in Anaheim (the same as Walt's) came from an old",
    "user_id": 8
}
```
---
### Ejemplo 3
**Request**  
```json
{
    "content": " ",
    "user_token": "9bf21297-9840-4539-b254-bb08a28dca24"
}
```
**Response**  
```json
{
    "detail": "content must not be empty"
}
```
---
### Ejemplo 4
**Request**  
```json
{
    "content": "Where is located Spain?",
    "user_token": "9bf21297-9840-4539-b254-bb08a28dca24",
    "response_length": 100,
    "response_temperature": 0.9,
    "response_top_p": 0.8,
    "response_top_k": 50 
}
```
**Response**  
```json
{
    "id": 28,
    "content": "Where is located Spain?",
    "generated_response": "\"Spain\".\nThe Spanish language has a very strong sense of history and culture. It's the most important part in our society, but it also contains many other things that are not easily understood by others (like religion). The word for this was 'Spanish'. In fact, I think we can say something like English or French if you want to understand what they mean better than us! So let me explain how my translation works",
    "user_id": 8
}
```


## 4. Ver el historial de chat del usuario
### Ejemplo 1
**Request**  
```json
{
    "token": "9bf21297-9840-4539-b254-bb08a28dca24"
}
```
**Response**  
```json
[
    {
        "id": 26,
        "content": "Hi, are you a gpt model?",
        "generated_response": "\"Yes. I am.\"\nI'm not sure if this is the same as what we're doing here but it's pretty clear that there was some sort",
        "user_id": 8
    },
    {
        "id": 27,
        "content": "Where is Disneyland World?",
        "generated_response": "\"Disneyland, California.\"\nThe answer to this question was a simple one. The Disney name for the park in Anaheim (the same as Walt's) came from an old",
        "user_id": 8
    }
]
```

## 5. Borrar el historial de chat del usuario
### Ejemplo 1
**Request**  
```json
{
    "token": "3d8c282f-7ace-4098-9635-1d1a458ad92e"
}
```
**Response**  
```
"Chat history deleted successfully"
```
