var PROTO_PATH = __dirname + '/../servidor/validadordocumento.proto'; // caminho do .proto
var readline = require('readline');//teclado
var grpc = require('@grpc/grpc-js');// biblioteca gRPC
var protoLoader = require('@grpc/proto-loader'); //caregador do.proto

// Carrega o .proto
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {keepCase: true,
     longs: String,
     enums: String,
     defaults: true,
     oneofs: true
    });
var validador_proto = grpc.loadPackageDefinition(packageDefinition).validadordocumento; // package do .proto

// Mensagem pelo código de erro
function traduzirResposta(response) {
  var mensagem;

  if (response.valido) {
    mensagem= 'Documento válido';
  } else if(response.erro === 0) {
    mensagem = 'Documento inválido';
  } else if(response.erro === 1.1) {
    mensagem = 'Estrutura da requisição inválida';
  } else if(response.erro=== 1.2){
    mensagem = 'Tipo de documento não informada';
  } else if (response.erro=== 1.3) {
    mensagem = 'Documento nao informado' ;
  } else if (response.erro === 2.1) {
    mensagem = 'Tipo de documento não processado';
  } else if (response.erro === 3.1){
    mensagem = 'Faltam dígitoos no documento';
  } else if (response.erro ===3.2){
    mensagem= 'Dígitos amais no documento';
  } else if (response.erro === 4.1) {
    mensagem= "Caractere invállido no documento" ;
  } else {
    mensagem = 'Erro desconhecido';
  }
  return mensagem;
}

function perguntarDocumento(client, leitor) {
  leitor.question('Tipo (1 = CPF, 2 = CNPJ, 0 = sair): ', function(tipo) {

    var tipo_doc = parseInt(tipo, 10);
    if (tipo_doc === 0) {
      leitor.close();
    } else {
      leitor.question('Documento: ', function(doc) {
        //Chamada remota
        //Lambrando queb essa função esta no srevidor
        client.Validar({tipo_doc:tipo_doc,doc: doc}, function(err, response) {
          if(err) {
            console.log('Erro de comunicação: ',err.message);
          }else{
            console.log('Resposta:', traduzirResposta(response));
          }
          perguntarDocumento(client, leitor);
        });
      });}
  });

}


// Cliente gRPC
function iniciarCliente() {
  var target = 'localhost:4851'; // endereço do servidor
  var client = new validador_proto.ValidadorDocumentos(target,grpc.credentials.createInsecure()); // cria o stub
  var leitor = readline.createInterface({input: process.stdin, output: process.stdout});
  perguntarDocumento(client, leitor);
}

iniciarCliente();