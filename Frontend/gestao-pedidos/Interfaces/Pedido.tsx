import { UUID } from "crypto";

export interface Pedido {
  id: UUID;
  cliente: string;
  valor: number;
  data_criacao: string;
  descricao: string;
}
