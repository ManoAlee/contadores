# Contadores Impressoras - Gestão Premium

Aplicação desktop moderna construída em Python (CustomTkinter) para monitoramento e gestão de contadores de impressoras Lexmark via protocolo SNMP.

![Badge](https://img.shields.io/badge/Status-Stable-green)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![UI](https://img.shields.io/badge/UI-CustomTkinter-blue)

## 🚀 Funcionalidades

-   **Dashboard Visual**: KPIs (Indicadores) de volume de impressão e gráficos de evolução mensal.
-   **Scan de Rede (SNMP)**: Busca automática de contadores das impressoras cadastradas via IP.
-   **Gestão de Impressoras**: Lista visual com status, modelo, setor e N/S (Número de Série).
-   **Alertas Inteligentes**: Notificações automáticas para manutenção baseada em volume de impressão.
-   **Dark Mode**: Interface moderna e agradável com tema escuro.

## 🛠️ Tecnologias

-   **Python 3.12+**
-   **CustomTkinter**: Interface Gráfica (GUI) moderna.
-   **PySNMP**: Comunicação de rede com as impressoras.
-   **Matplotlib**: Geração de gráficos.
-   **SQLite**: Banco de dados local para histórico.

## 📦 Instalação

1.  **Clone o repositório**
    ```bash
    git clone https://github.com/seu-usuario/contadores-impressoras.git
    cd contadores-impressoras
    ```

2.  **Crie o ambiente virtual**
    ```bash
    python -m venv .venv
    ```

3.  **Instale as dependências**
    ```bash
    .venv\Scripts\pip install -r app\requirements.txt
    ```

## ▶️ Como Usar

Execute o arquivo `start_gui.bat` (Windows) ou rode via terminal:

```bash
.venv\Scripts\python.exe run.py
```

### Configuração Inicial
1.  Ao abrir, vá na aba **Impressoras**.
2.  Clique em **📡 Scan de Rede (IP)** para buscar os dados reais da rede.
3.  (Opcional) Vá em **Configurações** para ajustar parâmetros de e-mail (se habilitado).

## 🔒 Segurança

Este projeto utiliza `keyring` para armazenamento seguro de credenciais locais e não commita dados sensíveis (banco de dados ou scripts de seed com IPs reais) no repositório.

## 🤝 Contribuição

1.  Faça um Fork do projeto.
2.  Crie uma Branch para sua Feature (`git checkout -b feature/IncrivelFeature`).
3.  Commit suas mudanças (`git commit -m 'Add some IncrivelFeature'`).
4.  Push para a Branch (`git push origin feature/IncrivelFeature`).
5.  Abra um Pull Request.

---
Desenvolvido com ❤️ por Automação.
