CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    conteudo TEXT NOT NULL,
    autor VARCHAR(100) DEFAULT 'Anônimo',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dados iniciais
INSERT INTO posts (titulo, conteudo, autor) VALUES
('Bem-vindo ao Blog', 'Este é o primeiro post do nosso blog. Bem-vindo!', 'Admin'),
('Docker Compose', 'Docker Compose é uma ferramenta para definir e executar aplicações multi-container.', 'Desenvolvedor'),
('Persistência de Dados', 'Aprenda como persistir dados com volumes Docker.', 'DevOps');