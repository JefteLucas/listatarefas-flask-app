# 📝 Gerenciador de Tarefas (To-Do List)

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-black)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

Aplicação web de lista de tarefas (to-do list) com autenticação de usuários, construída com **Flask** e **SQLAlchemy**. Cada usuário tem sua própria lista de tarefas, protegida por login — pensado para organizar pendências do dia a dia (trabalho, estudos, afazeres pessoais) com prioridade, status de conclusão e data de vencimento.

> 🎓 **Projeto estudantil.** Este projeto foi construído com o objetivo principal de **aprender na prática** conceitos de desenvolvimento web back-end: autenticação, segurança (CSRF, hashing de senha, variáveis de ambiente), modelagem de banco de dados e versionamento de schema. Não é (ainda) um produto em produção, mas sim um laboratório de estudo que evolui continuamente, com cada decisão técnica documentada e justificada ao longo do caminho.

---

## 🎯 Qual problema ele resolve

A ideia por trás do projeto é simples: a maioria das pessoas perde o controle de pequenas tarefas do dia a dia por falta de um lugar centralizado, seguro e rápido de consultar. O app busca resolver isso oferecendo:

- Um espaço **pessoal e seguro** para cada usuário (nenhum usuário vê ou altera tarefas de outro).
- Uma forma rápida de **priorizar** o que precisa ser feito primeiro.
- Visibilidade clara sobre o que já foi **concluído** e o que ainda está **pendente**.
- Um alerta simples para tarefas que passaram da **data de vencimento**.

---

## ✅ Funcionalidades implementadas

- [x] Cadastro de usuários com senha criptografada (hash, nunca em texto puro)
- [x] Login/logout com gerenciamento de sessão (Flask-Login)
- [x] Opção "Lembrar-me" (sessão persistente)
- [x] Criação, edição e exclusão de tarefas (CRUD completo)
- [x] Prioridade por tarefa (Baixa / Média / Alta), com destaque visual
- [x] Marcação de tarefas como concluídas
- [x] Isolamento de dados: cada usuário só acessa suas próprias tarefas
- [x] Proteção contra CSRF em todos os formulários
- [x] Variáveis de ambiente para dados sensíveis (chave secreta fora do código-fonte)
- [x] Normalização de e-mail (evita contas duplicadas por diferença de maiúsculas/minúsculas)
- [x] Páginas de erro customizadas (404, 403, 500)
- [x] Interface responsiva com Bootstrap 5

## 🚧 Em desenvolvimento

- [ ] Campo de data de vencimento (due date) nas tarefas, com aviso de tarefas atrasadas
- [ ] Versionamento de banco de dados com Flask-Migrate (migrations)
- [ ] Template base único (eliminação de duplicação entre as páginas)

## 🔜 Próximos passos (roadmap)

- [ ] Filtros e busca no dashboard (por status, prioridade, texto)
- [ ] Painel com estatísticas (total de tarefas, concluídas, pendentes, atrasadas)
- [ ] Edição de perfil e troca de senha
- [ ] Testes automatizados (pytest)
- [ ] Containerização com Docker
- [ ] Deploy em ambiente público (Render/Railway)

---

## 🛠️ Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Linguagem | Python 3 |
| Framework web | Flask |
| ORM / Banco de dados | Flask-SQLAlchemy + SQLite |
| Autenticação | Flask-Login |
| Segurança de formulários | Flask-WTF (proteção CSRF) |
| Hashing de senha | Werkzeug Security |
| Variáveis de ambiente | python-dotenv |
| Front-end | HTML5, Bootstrap 5, Jinja2 |

## 🔐 Segurança

Alguns cuidados aplicados ao longo do desenvolvimento, pensando em boas práticas reais de mercado:

- Senhas nunca são armazenadas em texto puro — apenas o hash (Werkzeug).
- A chave secreta da aplicação (`SECRET_KEY`) fica fora do código-fonte, carregada via variável de ambiente (`.env`, que não é versionado).
- Todos os formulários que alteram dados (criar, editar, excluir) são protegidos contra ataques CSRF.
- Ações destrutivas (como excluir tarefa) exigem requisição `POST`, nunca `GET`.
- Cada usuário só pode visualizar, editar ou excluir as próprias tarefas — verificado em todas as rotas protegidas.

## 🖥️ Como executar localmente

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd <pasta-do-projeto>

# 2. Crie e ative um ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Crie o arquivo .env na raiz do projeto com uma chave secreta
#    (gere uma com: python -c "import secrets; print(secrets.token_hex(32))")
echo SECRET_KEY=sua_chave_gerada_aqui > .env

# 5. Execute a aplicação
python app.py
```

Acesse `http://localhost:5000` no navegador. Um usuário administrador de teste é criado automaticamente na primeira execução (e-mail: `admin@email.com`).

> ⚠️ A senha padrão do usuário administrador é apenas um seed de desenvolvimento — recomendado trocar antes de qualquer uso além de testes locais.

## 📁 Estrutura do projeto

```
├── app.py                 # Aplicação Flask: rotas, modelos e configuração
├── requirements.txt        # Dependências do projeto
├── templates/              # Páginas HTML (Jinja2)
│   ├── index.html          # Login
│   ├── register.html       # Cadastro
│   ├── dashboard.html      # Lista de tarefas
│   ├── task_form.html      # Criação/edição de tarefa
│   ├── 404.html / 403.html / 500.html   # Páginas de erro
└── .env                    # Variáveis de ambiente (não versionado)
```

## 📷 Capturas de tela

*(adicionar prints do dashboard, login e formulário de tarefas aqui)*

---

## 🙋 Autor

Projeto desenvolvido por **[seu nome]** como parte do portfólio de estudos em desenvolvimento de sistemas.

Sinta-se à vontade para sugerir melhorias ou apontar problemas — este projeto está em constante evolução enquanto aprendo. 🚀
