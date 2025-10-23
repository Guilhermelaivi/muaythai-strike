from PIL import Image, ImageDraw, ImageFont
import io

def create_favicon():
    """Cria um favicon simples para a aplicação"""
    # Criar uma imagem 32x32 (tamanho padrão favicon)
    size = 32
    img = Image.new('RGB', (size, size), color='#FF6B35')  # Cor laranja do dojo
    
    # Desenhar um círculo branco no centro
    draw = ImageDraw.Draw(img)
    center = size // 2
    radius = size // 3
    
    # Círculo branco
    draw.ellipse([center - radius, center - radius, center + radius, center + radius], 
                 fill='white', outline='#F7931E', width=2)
    
    # Adicionar texto "D" no centro
    try:
        # Tentar usar uma fonte padrão
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        # Se não encontrar, usar fonte padrão
        font = ImageFont.load_default()
    
    # Desenhar a letra "D" de Dojo
    text = "D"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2
    
    # Desenhar o texto
    draw.text((text_x, text_y), text, fill='#FF6B35', font=font)
    
    return img

def save_favicon():
    """Salva o favicon como arquivo .ico"""
    img = create_favicon()
    
    # Salvar como ICO
    img.save('favicon.ico', format='ICO', sizes=[(32, 32)])
    
    # Também salvar como PNG para usar no Streamlit
    img.save('favicon.png', format='PNG')
    
    return True

if __name__ == "__main__":
    if save_favicon():
        print("✅ Favicon criado com sucesso!")
        print("📁 Arquivos: favicon.ico e favicon.png")
    else:
        print("❌ Erro ao criar favicon")