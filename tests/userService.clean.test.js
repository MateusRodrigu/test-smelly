const { UserService } = require('../src/userService');

describe('UserService - comportamentos públicos', () => {
  let userService;

  beforeEach(() => {
    userService = new UserService();
    userService._clearDB();
  });

  test('cria um usuário adulto ativo com os dados informados', () => {
    const dados = { nome: 'Alice', email: 'alice@teste.com', idade: 28 };

    const usuario = userService.createUser(dados.nome, dados.email, dados.idade);

    expect(usuario).toMatchObject({ ...dados, status: 'ativo', isAdmin: false });
    expect(usuario.id).toEqual(expect.any(String));
    expect(usuario.id).not.toHaveLength(0);
  });

  test('busca o usuário cadastrado pelo identificador retornado', () => {
    const usuario = userService.createUser('Alice', 'alice@teste.com', 28);

    const encontrado = userService.getUserById(usuario.id);

    expect(encontrado).toMatchObject({
      id: usuario.id,
      nome: 'Alice',
      email: 'alice@teste.com',
      idade: 28,
      status: 'ativo',
    });
  });

  test('desativa um usuário comum e mantém seu cadastro acessível', () => {
    const usuario = userService.createUser('Comum', 'comum@teste.com', 30);

    const resultado = userService.deactivateUser(usuario.id);

    expect(resultado).toBe(true);
    expect(userService.getUserById(usuario.id)).toMatchObject({
      id: usuario.id, status: 'inativo',
    });
  });

  test('preserva o administrador ativo ao recusar sua desativação', () => {
    const admin = userService.createUser('Admin', 'admin@teste.com', 40, true);

    const resultado = userService.deactivateUser(admin.id);

    expect(resultado).toBe(false);
    expect(userService.getUserById(admin.id)).toMatchObject({
      id: admin.id, status: 'ativo', isAdmin: true,
    });
  });

  test('inclui os usuários cadastrados no relatório sem exigir layout fixo', () => {
    const alice = userService.createUser('Alice', 'alice@teste.com', 28);
    const bob = userService.createUser('Bob', 'bob@teste.com', 32);

    const relatorio = userService.generateUserReport();

    expect(relatorio).toContain(alice.id);
    expect(relatorio).toContain('Alice');
    expect(relatorio).toContain(bob.id);
    expect(relatorio).toContain('Bob');
    expect(relatorio).toMatch(/\bativo\b/);
  });

  test('informa o estado inativo no relatório após a desativação', () => {
    const usuario = userService.createUser('Alice', 'alice@teste.com', 28);
    userService.deactivateUser(usuario.id);

    const relatorio = userService.generateUserReport();

    expect(relatorio).toContain(usuario.id);
    expect(relatorio).toContain('Alice');
    expect(relatorio).toMatch(/\binativo\b/);
    expect(relatorio).not.toMatch(/\bativo\b/);
  });

  test('rejeita o cadastro de usuário com 17 anos', () => {
    const cadastrarMenor = () => userService.createUser('Menor', 'menor@teste.com', 17);

    expect(cadastrarMenor).toThrow(/maior de idade/i);
  });

  test('aceita o cadastro no limite de 18 anos', () => {
    const idadeMinima = 18;

    const usuario = userService.createUser('Adulto', 'adulto@teste.com', idadeMinima);

    expect(usuario).toMatchObject({ idade: idadeMinima, status: 'ativo' });
  });

  test('informa a ausência de usuários no relatório de um banco vazio', () => {
    const mensagemEsperada = /nenhum usuário cadastrado/i;

    const relatorio = userService.generateUserReport();

    expect(relatorio).toMatch(mensagemEsperada);
  });
});
