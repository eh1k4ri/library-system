from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .book import BookResponse
from .user import UserResponse

class LoanEventResponse(BaseModel):
    id: int
    event_type: str # Para simplificar, usamos o nome do status novo como tipo
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Empréstimo ---

# Input: Só precisamos saber QUEM e QUAL LIVRO
class LoanCreate(BaseModel):
    user_id: int
    book_id: int
    days: int = 7 # Padrão de 7 dias, mas o front pode mudar

# Output: Retorna o objeto completo com status aninhado
class LoanResponse(BaseModel):
    id: int
    start_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status_slug: str # Vamos extrair o slug do relacionamento
    
    # Nested Objects (Opcional: trazer os dados do livro e usuário junto)
    book: BookResponse
    user: UserResponse
    events: List[LoanEventResponse] = []

    class Config:
        from_attributes = True

    # Hackzinho para pegar o status.slug flattenizado
    # O Pydantic v2 faz isso elegante, mas vamos manter simples:
    # O backend vai tratar isso na rota.