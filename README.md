# Gerador de notas para disciplinas

Este projeto é um Trabalho de Conclusão de Curso para o curso de Sistemas de Informação da Faculdade de Tecnologia da Unicamp. Este projeto objetiva gerar e adaptar conjuntos de dados para dois sistemas de mineração de dados educacionais em elaboração na Faculdade de Tecnologia da UNICAMP. O primeiro sistema é um visualizador de conjuntos de históricos escolares. O foco deste trabalho é desenvolver um gerador de conjuntos de históricos escolares simulados.
Esses conjuntos devem ter características programáveis, como por exemplo padrões específicos que se deseja que sejam possíveis de visualizar, e que serão derivadas de demandas de análise de dados já informadas por coordenadores de curso de graduação.

##### Áreas do conhecimento envolvidas no trabalho:
- Visualização da Informação
- Mineração de dados educacionais
---
#### Requisitos:
- [Python 3.x](https://www.python.org/download/releases/3.0/)
- [Pandas](https://pandas.pydata.org/)
- [Lista completa](https://github.com/gatihe/tcc-simulador/blob/master/requirements.txt)
#### Instruções:
- Faça o download e extração do repositório;
- Altere o arquivo pyrebase_config.py com as suas credenciais.
- Execute `pip install -r requirements.txt` no terminal;
- Execute `gsutil cors set cors.json gs://<your-cloud-storage-bucket>` no terminal
- Na raiz do diretório extraído, execute o arquivo `wsgi.py`;
- Importe um catálogo e, se necessário, configurações adicionais;
- Faça uma simulaçao;
- Exporte os relatórios.
---
### Manual do usuário:
#### Catálogos (.xml):

Entre as configurações que dão suporte à simulação de dados educacionais estão os catálogos de curso. Este arquivo tem como utilidade especificar as características do curso à ser simulado. Devem ser inseridos em `imports/catalogos/`. Um catálogo deve contar com a seguinte estrutura:


```
<all_configs>
	<cat_info>
		<course_id><ID_CURSO></course_id>
		<year><ANO_DO_CATALOGO></year>
		<max_years><TEMPO_MAXIMO_DE_DURACAO></max_years>
	</cat_info>
	<subjects>
		<subject>
			<id><ID_DISCIPLINA></id>
			<subject_name><NOME_DISCIPLINA></subject_name>
			<credits><QTDE_DE_CREDITOS></credits>
			<sem_offer><SEMESTRE_DE_OFERTA></sem_offer>
			<classes_no><NUMERO DE TURMAS></classes_no>
			<tipo_nivel_atividade_mae><NIVEL_ATIVIDADE_DA_DISCIPLINA></tipo_nivel_atividade_mae>
			<pre_reqs><PRE_REQUISITO></pre_reqs>
			<ano_inicio><ANO_DE_INICIO_DE_VIGENCIA_DO_PREREQ></ano_inicio>
			<ano_fim><ANO_DO_FIM_DE_VIGENCIA_DO_PREREQ></ano_fim>
			<no_cadeia_pre_requisito><NUM_CADEIA_DE_PRE_REQUISITOS></no_cadeia_pre_requisito>
			<tipo_pre_requisito><TIPO_PRE_REQUISITO></tipo_pre_requisito>
			<tipo_nivel_atividade_exigida><NIVEL_ATIVIDADE_EXIGIDA></tipo_nivel_atividade_exigida>
		</subject>
<all_configs>
```
- `<cat_info>`: Agrupa informações referentes ao catálogo;
- `<course_id>`: Identificador único do curso à ser simulado (int);
- `<year>`: Ano do catálogo (int);
- `<max_years>`: Tempo máximo que os alunos tem para concluir o curso (int);
- `<subjects>`:  Agrupa todas as disciplinas;
- `<subject>`: Agrupa informações referentes à uma disciplina;
- `<id>`: Identificador único da disciplina a ser simulada (int);
- `<subject_name>`: Nome da disciplina (string);
- `<credits>`: Quantidade de créditos referentes à disciplina (int);
- `<sem_offer>`: Semestre em que a disciplina é ofertada aos alunos (int);
- `<classes_no>`: Quantidade de turmas em paralelo na oferta (int);
- `<tipo_nivel_atividade_mae>`: Natureza da disciplina, pode ser 'G' para se referir à graduação, 'P' para pós-graduação ou qualquer outro valor desejado (chr);
- `<pre_reqs>`: Identificador único da disciplina que seja pré-requisito da disciplina em questão. Mesmo que não haja algum pré-requisito, é necessário ao menos uma instância dessa tag por disciplina (string ou vazio caso não haja). Para disciplinas com mais de um pré-requisito, repetir em ordem correta esta tag e as tags abaixo;
- `<ano_inicio>`: Ano em que se iniciou a vigência do pré-requisito em questão. Mesmo que não haja algum pré-requisito, é necessário ao menos uma instância dessa tag por disciplina (int ou vazio caso não haja);
- `<ano_fim>`: Ano em que se encerrou a vigência do pré-requisito em questão ('0' caso vigência do pré-requisito ainda não tenha encerrado). Mesmo que não haja algum pré-requisito, é necessário ao menos uma instância dessa tag por disciplina (int ou vazio caso não haja);
- `<no_cadeia_pre_requisito>`: Identificador único da cadeia de requisitos à qual este pré-requisito pertence (int);
- `<tipo_pre_requisito>`: O tipo de pré-requisito definirá se para cursar a disciplina, o aluno deve ter passado no pré-requisito ou ao menos cursado ('FORTE' para disciplinas que exigem aprovação no pré-requisito, 'FRACO' para disciplinas que exigem somente matrícula anterior na disciplina);
- `<tipo_nivel_atividade_exigida>`: Natureza do pré-requisito, pode ser 'G' para se referir à graduação, 'P' para pós-graduação ou qualquer outro valor desejado (chr).

#### Configurações adicionais (.xml):

É possível adicionar configurações adicionais para adaptar o comportamento do simulador. Devem ser inseridos em `imports/configs/`.Segue estrutura de um arquivo de configurações adicionais:

```
<all_configs>
  <generic_info>
    <ano_ingresso>ANO_DE_INGRESSO</ano_ingresso>
  </generic_info>
  <parameters>
    <parameter>
      <parameter_name>NOME_PARAMETRO</parameter_name>
      <min_grade>NOTA_MINIMA</min_grade>
      <max_grade>NOTA_MAXIMA</max_grade>
      <qtde>QTDE_ALUNOS</qtde>
    </parameter>
  </parameters>
  <factors>
    <easy_pass_factor>FATOR_FACILITADOR</easy_pass_factor>
    <hard_pass_factor>FATOR_DESFAVORÁVEL</hard_pass_factor>
  </factors>
  <subj_dificulty>
    <hard_pass>
      <sub_id>ID_DISCIPLINA</sub_id>
    </hard_pass>
    <easy_pass>
      <sub_id>ID_DISCIPLINA</sub_id>
    </easy_pass>
  </subj_dificulty>
</all_configs>
```
- `<all_configs>`: Agrupa todas informações referentes à configurações adicionais do sistema;
- `<generic_info>`: Agrupa informações gerais da turma à ser simulada;
- `<ano_ingresso>`: Ano de ingresso da turma à ser simulada (int);
- `<parameters>`: Agrupa todos os parâmetros à serem adotados durante a simulação. Deve haver pelo menos um parâmetro populado;
- `<parameter>`: Agrupa informações de uma instância de parâmetro;
- `<parameter_name>`: Identificador único do parâmetro (string);
- `<min_grade>`: Nota mínima à ser sorteada pelo parâmetro. Pode sofrer redução devido a configuração de outros fatores (float);
- `<max_grade>`: Nota máxima à ser sorteada pelo parâmetro. Pode sofrer redução devido a configuração de outros fatores (float);
- `<qtde>`: Quantidade de alunos à serem sorteados neste parâmetro (int);
- `<factors>`: Agrupa configurações dos fatores que irão impactar positivamente e negativamente as notas simuladas;
- `<easy_pass_factor>`: Aponta o máximo que a nota do aluno poderá variar positivamente (0 à easy_pass_factor) caso a disciplina cursada esteja listada em `<easy_pass>` (int);
- `<hard_pass_factor>`: Aponta o máximo que a nota do aluno poderá variar negativamente (0 à easy_pass_factor) caso a disciplina cursada esteja listada em `<easy_pass>` (int);
- `<subj_dificulty>`: Agrupa os grupos de disciplinas que sofrerão alteração na nota;
- `<hard_pass>`: Agrupa disciplinas que sofrerão impacto negativo na nota;
- `<easy_pass>`: Agrupa disciplinas que sofrerão impacto positivo na nota;
- `<sub_id>`: Identificador único da disciplina a ser incluída em um dos grupos (string).

---
#### Contato:

Entre em contato através do [e-mail](mailto:atihe.guilherme@gmail.com) para tirar dúvidas à respeito da aplicação. Caso encontre algum bug ou mal-funcionamento, por favor criar um [issue](https://github.com/gatihe/simulador/issues).
