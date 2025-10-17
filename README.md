# Match Trampo Backend API

Este é o projeto de backend para o aplicativo Match Trampo, desenvolvido em Flask com SQLAlchemy (SQLite) para prototipação.

## Funcionalidades Implementadas

*   **API REST** para gerenciamento de Profissionais, Assinaturas e Agendamentos.
*   **Lógica de Ranqueamento (RF 2.3.2):** Busca por profissão e localização, ranqueando por Plano Master e Avaliação.
*   **Lógica de Assinatura (RF 2.9):** Verificação de status e simulação de pagamento/reativação.
*   **Lógica de Agendamento (RF 2.5 e 2.8.3):** Bloqueio de 2 horas e liberação ("Visita Encerrada").

## Como Rodar Localmente

Siga os passos abaixo para iniciar o backend e o frontend.

### 1. Pré-requisitos

*   Python 3.10+
*   Node.js ou Bun (para o frontend)

### 2. Configuração do Backend

1.  **Navegue até o diretório do backend:**
    ```bash
    cd match-trampo-backend
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install Flask Flask-SQLAlchemy Flask-CORS
    ```

4.  **Inicialize o banco de dados e rode o servidor:**
    O banco de dados SQLite será criado e populado com dados de teste automaticamente.
    ```bash
    python app.py
    ```
    O servidor estará rodando em `http://localhost:5000`.

### 3. Configuração do Frontend

1.  **Abra uma nova janela do terminal e navegue até o diretório do frontend:**
    ```bash
    cd ../match-servico-ja
    ```

2.  **Instale as dependências (usando npm ou bun):**
    ```bash
    npm install
    # ou
    # bun install
    ```

3.  **Rode o servidor de desenvolvimento:**
    ```bash
    npm run dev
    ```
    O frontend estará rodando em `http://localhost:8080`.

### 4. Testes Práticos

Para verificar as funcionalidades implementadas, acesse o frontend e navegue para as seguintes URLs:

*   **Página Inicial:** `http://localhost:8080/`
    *   Aqui você pode testar a lógica de Bloqueio de Agendamento.
*   **Página de Perfil (Dados do DB):** `http://localhost:8080/profile/prof_123`
    *   Verifique se os dados do profissional (João da Silva, Eletricista, São Paulo) estão sendo carregados do backend.

**Endpoints da API para Teste (cURL ou Postman):**

*   **Buscar Profissionais (Ranqueamento):**
    ```bash
    curl "http://localhost:5000/api/search/professionals?profession=Eletricista&city=São%20Paulo"
    ```
*   **Verificar Assinatura (Ativa):**
    ```bash
    curl http://localhost:5000/api/payment/subscription/prof_123
    ```
*   **Verificar Assinatura (Inadimplente):**
    ```bash
    curl http://localhost:5000/api/payment/subscription/prof_789
    ```
*   **Bloquear Agendamento:**
    ```bash
    curl -X POST http://localhost:5000/api/schedule/block -H "Content-Type: application/json" -d '{"professional_id": "prof_123", "start_time": "2025-10-25T10:00:00"}'
    ```

---
**Próximos Passos (Sugestão de Desenvolvimento):**

1.  Implementar a interface de Agendamento na Página de Perfil.
2.  Criar a interface de Busca e a lista de resultados na página inicial.
3.  Implementar a lógica de Geolocalização (RF 2.10).
