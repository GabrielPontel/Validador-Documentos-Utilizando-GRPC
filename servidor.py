from concurrent import futures
import logging
import grpc
import validadordocumento_pb2 
import validadordocumento_pb2_grpc  

# Serviço gRPC (implementa o service do .proto)
class ValidadorDocumentos(validadordocumento_pb2_grpc.ValidadorDocumentosServicer):

    # Metodo camado pelo cliente
    def Validar(self, requisicao, contexto):
        valido, erro = self.validar_documento(requisicao.tipo_doc, requisicao.doc)
        print(f"Recebido: tipo_doc+{requisicao.tipo_doc}&doc+{requisicao.doc} ->Enviado: valido+{int(valido)}&erro+{erro}")
        
        # Mensagem de resposta do .proto
        resposta = validadordocumento_pb2.ResultadoResponse(valido=valido, erro=erro)
        return resposta

    def validar_documento(self, tipo_documento, numero_documento):
        #Vadlida o docuemto enviado pelo user.
        #tipo_documento: 1 = CPF ou2 = CNPJ
        
        quantidade_digitos = {1:11, 2: 14}
        valido =False
        erro=0.0
        if tipo_documento ==0:
            erro =1.2
        elif numero_documento == "":
            erro=1.3
        elif tipo_documento not in quantidade_digitos:
            erro=2.1
        elif not numero_documento.isdigit():
            erro= 4.1
        elif len(numero_documento) < quantidade_digitos[tipo_documento]:
            erro =3.1
        elif len(numero_documento) > quantidade_digitos[tipo_documento]:
            erro =3.2
        elif tipo_documento==1:
            valido =self.verificar_digitos_cpf(numero_documento)
        else:
            valido = self.verificar_digitos_cnpj(numero_documento)

        return valido, erro

    def verificar_digitos_cpf(self, cpf):
        #Confere os dois dígitos verificadores do CPF.
        digitos_corretos = True
        if cpf == cpf[0] *11:
            digitos_corretos= False
        else:
            for posicao_digito in (9, 10):
                soma = 0
                for indice in range(posicao_digito):
                    peso = (posicao_digito + 1) - indice
                    soma += int(cpf[indice]) * peso
                digito_calculado = (soma * 10 % 11) % 10
                if digito_calculado != int(cpf[posicao_digito]):
                    digitos_corretos = False
        return digitos_corretos

    def verificar_digitos_cnpj(self, cnpj):
        #Confere os dois dígitos verificadores do CNPJ.
        pesos_primeiro_digito = [5,4,3,2,9,8, 7,6,5, 4, 3, 2]
        pesos_segundo_digito = [6,5,4,3,2,9,8,7,6, 5, 4, 3, 2]
        digitos_corretos =True

        if cnpj == cnpj[0] * 14:
            digitos_corretos= False
        else:
            for pesos, posicao_digito in ((pesos_primeiro_digito, 12), (pesos_segundo_digito, 13)):
                soma =0
                for indice in range(posicao_digito):
                    soma+= int(cnpj[indice]) * pesos[indice]
                resto =soma % 11
                if resto < 2:
                    digito_calculado = 0
                else:
                    digito_calculado = 11 - resto

                if digito_calculado != int(cnpj[posicao_digito]):
                    digitos_corretos = False
        return digitos_corretos


# ServidorgRPC
def iniciar_servidor():
    porta = "4851"
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10)) #cria oservidor
    validadordocumento_pb2_grpc.add_ValidadorDocumentosServicer_to_server(ValidadorDocumentos(), servidor)  #registra o serviço
    servidor.add_insecure_port("[::]:" + porta)# abre a porta
    servidor.start()  # inicia
    print("Servidor iniciado, escutando na porta " + porta)
    servidor.wait_for_termination() #mantem rodado


if __name__ == "__main__":
    logging.basicConfig()#mostra us erros internosgRPC
    iniciar_servidor()