// CW Transportadora - Main JavaScript

// Screen content templates
const screens = {
  dashboard: `
    <div class="page-header">
      <h1 class="page-title">Dashboard Executivo</h1>
      <p class="page-description">Visão geral das operações e métricas em tempo real</p>
    </div>
    
    <div class="filters">
      <button class="btn btn-primary btn-sm">Hoje</button>
      <button class="btn btn-secondary btn-sm">Semana</button>
      <button class="btn btn-secondary btn-sm">Mês</button>
      <button class="btn btn-secondary btn-sm">Ano</button>
      <button class="btn btn-secondary btn-sm">Personalizado</button>
    </div>
    
    <div class="grid grid-6" style="margin-bottom: 32px;">
      <div class="kpi-card">
        <div class="kpi-label">Faturamento Total</div>
        <div class="kpi-value">R$ 1.234.567</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +12.5%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Viagens Realizadas</div>
        <div class="kpi-value">847</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +8.3%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Notas Processadas</div>
        <div class="kpi-value">12.456</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +15.2%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Custos Operacionais</div>
        <div class="kpi-value">R$ 456.789</div>
        <div class="kpi-trend negative">
          <img src="assets/icons/chevron-down.svg" alt="down" width="16" height="16">
          +3.2%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Lucro Líquido</div>
        <div class="kpi-value">R$ 777.778</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +18.7%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Margem de Lucro</div>
        <div class="kpi-value">63.1%</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +2.4%
        </div>
      </div>
    </div>
    
    <div class="grid grid-6" style="margin-bottom: 32px;">
      <div class="kpi-card">
        <div class="kpi-label">Clientes Ativos</div>
        <div class="kpi-value">234</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +5.1%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Veículos em Operação</div>
        <div class="kpi-value">42</div>
        <div class="kpi-trend negative">
          <img src="assets/icons/chevron-down.svg" alt="down" width="16" height="16">
          -2
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Motoristas Ativos</div>
        <div class="kpi-value">56</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +3
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Média por Viagem</div>
        <div class="kpi-value">R$ 1.457</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +4.2%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Entregas no Prazo</div>
        <div class="kpi-value">94.5%</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +1.8%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Ticket Médio</div>
        <div class="kpi-value">R$ 5.278</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +6.3%
        </div>
      </div>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 32px;">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Faturamento Mensal</h3>
        </div>
        <div class="card-body">
          <div class="chart-placeholder">Gráfico de Linha - Faturamento</div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Viagens por Região</h3>
        </div>
        <div class="card-body">
          <div class="chart-placeholder">Gráfico de Barra - Regiões</div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Distribuição de Custos</h3>
        </div>
        <div class="card-body">
          <div class="chart-placeholder">Gráfico de Pizza - Custos</div>
        </div>
      </div>
    </div>
    
    <div class="grid grid-2">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Volume de Notas</h3>
        </div>
        <div class="card-body">
          <div class="chart-placeholder">Gráfico de Área - Notas</div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Performance da Frota</h3>
        </div>
        <div class="card-body">
          <div class="chart-placeholder">Gráfico de Linha - Frota</div>
        </div>
      </div>
    </div>
  `,
  
  notas: `
    <div class="page-header">
      <h1 class="page-title">Notas/Manifestos</h1>
      <p class="page-description">Gerenciamento de notas fiscais e manifestos de transporte</p>
    </div>
    
    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Importar Arquivo TXT</h3>
      </div>
      <div class="card-body">
        <div style="border: 2px dashed var(--color-border); border-radius: var(--radius-md); padding: 32px; text-align: center;">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--color-text-tertiary); margin-bottom: 16px;">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <p style="color: var(--color-text-secondary); margin-bottom: 16px;">Arraste e solte o arquivo TXT ou clique para selecionar</p>
          <button class="btn btn-primary">Selecionar Arquivo</button>
        </div>
      </div>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Período:</label>
        <select class="form-select" style="width: auto;">
          <option>Últimos 7 dias</option>
          <option>Últimos 30 dias</option>
          <option>Este mês</option>
          <option>Mês anterior</option>
        </select>
      </div>
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Cliente:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>Cliente A</option>
          <option>Cliente B</option>
        </select>
      </div>
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Status:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>Disponível</option>
          <option>Em viagem</option>
          <option>Entregue</option>
        </select>
      </div>
      <button class="btn btn-primary">
        <img src="assets/icons/filter.svg" alt="Filtro" width="16" height="16">
        Aplicar Filtros
      </button>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 24px;">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Manifesto #001</h3>
          <span class="badge badge-info">Disponível</span>
        </div>
        <div class="card-body">
          <p><strong>Cliente:</strong> Empresa ABC Ltda</p>
          <p><strong>Notas:</strong> 45 notas</p>
          <p><strong>Peso Total:</strong> 12.450 kg</p>
          <p><strong>Valor:</strong> R$ 45.678,90</p>
        </div>
        <div class="card-footer">
          <button class="btn btn-primary btn-sm">Ver Detalhes</button>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Manifesto #002</h3>
          <span class="badge badge-warning">Em viagem</span>
        </div>
        <div class="card-body">
          <p><strong>Cliente:</strong> Comércio XYZ</p>
          <p><strong>Notas:</strong> 32 notas</p>
          <p><strong>Peso Total:</strong> 8.780 kg</p>
          <p><strong>Valor:</strong> R$ 32.456,78</p>
        </div>
        <div class="card-footer">
          <button class="btn btn-primary btn-sm">Acompanhar</button>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Manifesto #003</h3>
          <span class="badge badge-success">Entregue</span>
        </div>
        <div class="card-body">
          <p><strong>Cliente:</strong> Indústria DEF</p>
          <p><strong>Notas:</strong> 28 notas</p>
          <p><strong>Peso Total:</strong> 6.540 kg</p>
          <p><strong>Valor:</strong> R$ 28.345,67</p>
        </div>
        <div class="card-footer">
          <button class="btn btn-primary btn-sm">Ver Detalhes</button>
        </div>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Lista de Notas</h3>
        <button class="btn btn-outline btn-sm">
          <img src="assets/icons/export.svg" alt="Exportar" width="16" height="16">
          Exportar
        </button>
      </div>
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Número</th>
              <th>Cliente</th>
              <th>Valor</th>
              <th>Peso</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-mono">NF-001234</td>
              <td>Empresa ABC Ltda</td>
              <td class="font-mono">R$ 1.234,56</td>
              <td class="font-mono">450 kg</td>
              <td><span class="badge badge-info">Disponível</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td class="font-mono">NF-001235</td>
              <td>Comércio XYZ</td>
              <td class="font-mono">R$ 2.345,67</td>
              <td class="font-mono">680 kg</td>
              <td><span class="badge badge-warning">Em viagem</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td class="font-mono">NF-001236</td>
              <td>Indústria DEF</td>
              <td class="font-mono">R$ 987,65</td>
              <td class="font-mono">320 kg</td>
              <td><span class="badge badge-success">Entregue</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  'nova-operacao': `
    <div class="page-header">
      <h1 class="page-title">Nova Operação</h1>
      <p class="page-description">Criar nova operação de transporte (SP → Cascavel)</p>
    </div>
    
    <div class="grid grid-3">
      <div class="card" style="grid-column: span 2;">
        <div class="card-header">
          <h3 class="card-title">Dados da Operação</h3>
        </div>
        <div class="card-body">
          <form>
            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">Data</label>
                <input type="date" class="form-input">
              </div>
              <div class="form-group">
                <label class="form-label">Caminhão</label>
                <select class="form-select">
                  <option>Selecione...</option>
                  <option>ABC-1234 - Volvo FH</option>
                  <option>DEF-5678 - Scania R</option>
                </select>
              </div>
            </div>
            
            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">Placa</label>
                <input type="text" class="form-input" placeholder="ABC-1234">
              </div>
              <div class="form-group">
                <label class="form-label">Motorista</label>
                <select class="form-select">
                  <option>Selecione...</option>
                  <option>João Silva</option>
                  <option>Maria Santos</option>
                </select>
              </div>
            </div>
            
            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">Valor do Frete (R$)</label>
                <input type="number" class="form-input" placeholder="0,00">
              </div>
              <div class="form-group">
                <label class="form-label">Peso Total (kg)</label>
                <input type="number" class="form-input" placeholder="0">
              </div>
            </div>
            
            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">Combustível (R$)</label>
                <input type="number" class="form-input" placeholder="0,00">
              </div>
              <div class="form-group">
                <label class="form-label">Pedágio (R$)</label>
                <input type="number" class="form-input" placeholder="0,00">
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">Observações</label>
              <textarea class="form-textarea" placeholder="Observações adicionais..."></textarea>
            </div>
            
            <div class="actions" style="margin-top: 24px;">
              <button type="button" class="btn btn-secondary">Cancelar</button>
              <button type="submit" class="btn btn-primary">Salvar Operação</button>
            </div>
          </form>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Resumo de Custos</h3>
        </div>
        <div class="card-body">
          <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Frete</span>
              <span class="font-mono">R$ 0,00</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Combustível</span>
              <span class="font-mono">R$ 0,00</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Pedágio</span>
              <span class="font-mono">R$ 0,00</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Outros</span>
              <span class="font-mono">R$ 0,00</span>
            </div>
            <hr style="border: none; border-top: 1px solid var(--color-border); margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; font-weight: 600;">
              <span>Total de Custos</span>
              <span class="font-mono">R$ 0,00</span>
            </div>
            <hr style="border: none; border-top: 1px solid var(--color-border); margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; font-weight: 700; font-size: 18px;">
              <span>Lucro Estimado</span>
              <span class="font-mono" style="color: var(--color-success);">R$ 0,00</span>
            </div>
          </div>
        </div>
        
        <div class="card-header" style="margin-top: 24px;">
          <h3 class="card-title">Histórico Recente</h3>
        </div>
        <div class="card-body">
          <div style="font-size: 13px;">
            <div style="padding: 8px 0; border-bottom: 1px solid var(--color-border-light);">
              <div style="font-weight: 500;">Operação #1234</div>
              <div class="text-secondary">SP → Cascavel</div>
              <div class="font-mono text-tertiary">R$ 4.500,00</div>
            </div>
            <div style="padding: 8px 0; border-bottom: 1px solid var(--color-border-light);">
              <div style="font-weight: 500;">Operação #1233</div>
              <div class="text-secondary">SP → Curitiba</div>
              <div class="font-mono text-tertiary">R$ 3.800,00</div>
            </div>
            <div style="padding: 8px 0;">
              <div style="font-weight: 500;">Operação #1232</div>
              <div class="text-secondary">SP → Porto Alegre</div>
              <div class="font-mono text-tertiary">R$ 5.200,00</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  
  'criar-viagem': `
    <div class="page-header">
      <h1 class="page-title">Criar Viagem</h1>
      <p class="page-description">Organizar notas em uma nova viagem</p>
    </div>
    
    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Selecionar Cliente</h3>
      </div>
      <div class="card-body">
        <div class="form-group">
          <label class="form-label">Buscar Cliente</label>
          <input type="text" class="form-input" placeholder="Digite o nome do cliente...">
        </div>
      </div>
    </div>
    
    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Notas Disponíveis - Empresa ABC Ltda</h3>
      </div>
      <div class="card-body">
        <div class="grid grid-3">
          <div class="card" style="border: 2px solid var(--color-border);">
            <div class="card-body">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span class="font-mono" style="font-weight: 600;">NF-001234</span>
                <input type="checkbox" checked>
              </div>
              <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Valor: <span class="font-mono">R$ 1.234,56</span></p>
              <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Peso: <span class="font-mono">450 kg</span></p>
              <p class="text-secondary" style="font-size: 13px;">Destino: Cascavel, PR</p>
            </div>
          </div>
          <div class="card" style="border: 2px solid var(--color-border);">
            <div class="card-body">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span class="font-mono" style="font-weight: 600;">NF-001235</span>
                <input type="checkbox" checked>
              </div>
              <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Valor: <span class="font-mono">R$ 2.345,67</span></p>
              <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Peso: <span class="font-mono">680 kg</span></p>
              <p class="text-secondary" style="font-size: 13px;">Destino: Cascavel, PR</p>
            </div>
          </div>
          <div class="card" style="border: 2px solid var(--color-border);">
            <div class="card-body">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span class="font-mono" style="font-weight: 600;">NF-001236</span>
                <input type="checkbox">
              </div>
              <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Valor: <span class="font-mono">R$ 987,65</span></p>
              <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Peso: <span class="font-mono">320 kg</span></p>
              <p class="text-secondary" style="font-size: 13px;">Destino: Foz do Iguaçu, PR</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid grid-3">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Capacidade do Caminhão</h3>
        </div>
        <div class="card-body">
          <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Peso Carregado</span>
              <span class="font-mono">1.130 kg</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Capacidade Máxima</span>
              <span class="font-mono">15.000 kg</span>
            </div>
            <div style="background: var(--color-surface); border-radius: var(--radius-md); height: 8px; margin: 12px 0;">
              <div style="background: var(--color-primary); border-radius: var(--radius-md); height: 100%; width: 7.5%;"></div>
            </div>
            <div style="font-size: 12px; color: var(--color-text-tertiary);">7.5% da capacidade</div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Resumo da Viagem</h3>
        </div>
        <div class="card-body">
          <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Notas Selecionadas</span>
              <span class="font-mono">2</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Peso Total</span>
              <span class="font-mono">1.130 kg</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Valor Total</span>
              <span class="font-mono">R$ 3.580,23</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Ações</h3>
        </div>
        <div class="card-body">
          <div class="actions flex-col gap-md">
            <button class="btn btn-primary">Criar Viagem</button>
            <button class="btn btn-secondary">Salvar Rascunho</button>
            <button class="btn btn-ghost">Cancelar</button>
          </div>
          <p class="text-tertiary" style="font-size: 12px; margin-top: 16px;">Rascunho salvo automaticamente</p>
        </div>
      </div>
    </div>
  `,
  
  viagens: `
    <div class="page-header">
      <h1 class="page-title">Histórico de Viagens</h1>
      <p class="page-description">Todas as viagens realizadas e em andamento</p>
    </div>
    
    <div class="grid grid-4" style="margin-bottom: 24px;">
      <div class="kpi-card">
        <div class="kpi-label">Total de Viagens</div>
        <div class="kpi-value">847</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Notas Transportadas</div>
        <div class="kpi-value">12.456</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Frete Total</div>
        <div class="kpi-value">R$ 1.234.567</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Peso Total</div>
        <div class="kpi-value">2.345.678 kg</div>
      </div>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Período:</label>
        <select class="form-select" style="width: auto;">
          <option>Últimos 7 dias</option>
          <option>Últimos 30 dias</option>
          <option>Este mês</option>
          <option>Mês anterior</option>
        </select>
      </div>
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Status:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>Em andamento</option>
          <option>Concluída</option>
          <option>Cancelada</option>
        </select>
      </div>
      <button class="btn btn-primary">
        <img src="assets/icons/filter.svg" alt="Filtro" width="16" height="16">
        Aplicar Filtros
      </button>
    </div>
    
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Origem</th>
              <th>Destino</th>
              <th>Data</th>
              <th>Motorista</th>
              <th>Notas</th>
              <th>Valor</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-mono">#V001</td>
              <td>São Paulo, SP</td>
              <td>Cascavel, PR</td>
              <td class="font-mono">13/08/2026</td>
              <td>João Silva</td>
              <td class="font-mono">45</td>
              <td class="font-mono">R$ 45.678,90</td>
              <td><span class="badge badge-warning">Em andamento</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Finalizar">
                    <img src="assets/icons/check.svg" alt="Check" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td class="font-mono">#V002</td>
              <td>São Paulo, SP</td>
              <td>Curitiba, PR</td>
              <td class="font-mono">12/08/2026</td>
              <td>Maria Santos</td>
              <td class="font-mono">32</td>
              <td class="font-mono">R$ 32.456,78</td>
              <td><span class="badge badge-success">Concluída</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td class="font-mono">#V003</td>
              <td>São Paulo, SP</td>
              <td>Porto Alegre, RS</td>
              <td class="font-mono">11/08/2026</td>
              <td>Carlos Oliveira</td>
              <td class="font-mono">28</td>
              <td class="font-mono">R$ 28.345,67</td>
              <td><span class="badge badge-success">Concluída</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  ranking: `
    <div class="page-header">
      <h1 class="page-title">Ranking de Clientes</h1>
      <p class="page-description">Classificação dos clientes por volume e valor</p>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 24px;">
      <div class="kpi-card">
        <div class="kpi-label">Total de Clientes</div>
        <div class="kpi-value">234</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Volume Total</div>
        <div class="kpi-value">R$ 1.234.567</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Ticket Médio</div>
        <div class="kpi-value">R$ 5.278</div>
      </div>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Período:</label>
        <select class="form-select" style="width: auto;">
          <option>Últimos 7 dias</option>
          <option>Últimos 30 dias</option>
          <option>Este mês</option>
          <option>Mês anterior</option>
        </select>
      </div>
      <button class="btn btn-outline">
        <img src="assets/icons/export.svg" alt="Exportar" width="16" height="16">
        Exportar CSV
      </button>
    </div>
    
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Posição</th>
              <th>Cliente</th>
              <th>Viagens</th>
              <th>Notas</th>
              <th>Volume (kg)</th>
              <th>Valor Total</th>
              <th>Ticket Médio</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="badge badge-primary">1º</span></td>
              <td>Empresa ABC Ltda</td>
              <td class="font-mono">156</td>
              <td class="font-mono">2.345</td>
              <td class="font-mono">456.789</td>
              <td class="font-mono">R$ 456.789,00</td>
              <td class="font-mono">R$ 2.928,00</td>
            </tr>
            <tr>
              <td><span class="badge badge-primary">2º</span></td>
              <td>Comércio XYZ</td>
              <td class="font-mono">134</td>
              <td class="font-mono">1.987</td>
              <td class="font-mono">345.678</td>
              <td class="font-mono">R$ 345.678,00</td>
              <td class="font-mono">R$ 2.579,00</td>
            </tr>
            <tr>
              <td><span class="badge badge-primary">3º</span></td>
              <td>Indústria DEF</td>
              <td class="font-mono">98</td>
              <td class="font-mono">1.456</td>
              <td class="font-mono">234.567</td>
              <td class="font-mono">R$ 234.567,00</td>
              <td class="font-mono">R$ 2.394,00</td>
            </tr>
            <tr>
              <td><span class="badge badge-secondary">4º</span></td>
              <td>Distribuidora GHI</td>
              <td class="font-mono">87</td>
              <td class="font-mono">1.234</td>
              <td class="font-mono">198.765</td>
              <td class="font-mono">R$ 198.765,00</td>
              <td class="font-mono">R$ 2.285,00</td>
            </tr>
            <tr>
              <td><span class="badge badge-secondary">5º</span></td>
              <td>Transportadora JKL</td>
              <td class="font-mono">76</td>
              <td class="font-mono">1.123</td>
              <td class="font-mono">187.654</td>
              <td class="font-mono">R$ 187.654,00</td>
              <td class="font-mono">R$ 2.469,00</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  combustivel: `
    <div class="page-header">
      <h1 class="page-title">Controle de Combustível</h1>
      <p class="page-description">Registro e monitoramento de abastecimentos</p>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 24px;">
      <div class="kpi-card">
        <div class="kpi-label">Consumo Médio</div>
        <div class="kpi-value">8.5 km/L</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +0.3 km/L
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Gasto Total (Mês)</div>
        <div class="kpi-value">R$ 45.678</div>
        <div class="kpi-trend negative">
          <img src="assets/icons/chevron-down.svg" alt="down" width="16" height="16">
          +5.2%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Litros Abastecidos</div>
        <div class="kpi-value">12.345 L</div>
        <div class="kpi-trend positive">
          <img src="assets/icons/chevron-down.svg" alt="up" width="16" height="16" style="transform: rotate(180deg);">
          +2.1%
        </div>
      </div>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Período:</label>
        <select class="form-select" style="width: auto;">
          <option>Últimos 7 dias</option>
          <option>Últimos 30 dias</option>
          <option>Este mês</option>
          <option>Mês anterior</option>
        </select>
      </div>
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Veículo:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>ABC-1234</option>
          <option>DEF-5678</option>
        </select>
      </div>
      <button class="btn btn-primary">Novo Abastecimento</button>
    </div>
    
    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Consumo ao Longo do Tempo</h3>
      </div>
      <div class="card-body">
        <div class="chart-placeholder">Gráfico de Linha - Consumo</div>
      </div>
    </div>
    
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Veículo</th>
              <th>Motorista</th>
              <th>Litros</th>
              <th>Valor/L</th>
              <th>Total</th>
              <th>Km Rodados</th>
              <th>Km/L</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-mono">13/08/2026</td>
              <td class="font-mono">ABC-1234</td>
              <td>João Silva</td>
              <td class="font-mono">250 L</td>
              <td class="font-mono">R$ 5,89</td>
              <td class="font-mono">R$ 1.472,50</td>
              <td class="font-mono">2.125 km</td>
              <td class="font-mono">8,5 km/L</td>
            </tr>
            <tr>
              <td class="font-mono">12/08/2026</td>
              <td class="font-mono">DEF-5678</td>
              <td>Maria Santos</td>
              <td class="font-mono">280 L</td>
              <td class="font-mono">R$ 5,89</td>
              <td class="font-mono">R$ 1.649,20</td>
              <td class="font-mono">2.380 km</td>
              <td class="font-mono">8,5 km/L</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  manutencao: `
    <div class="page-header">
      <h1 class="page-title">Manutenção da Frota</h1>
      <p class="page-description">Controle de revisões e oficinas</p>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 24px;">
      <div class="kpi-card">
        <div class="kpi-label">Custo Total (Mês)</div>
        <div class="kpi-value">R$ 12.345</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Manutenções Realizadas</div>
        <div class="kpi-value">8</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Alertas Ativos</div>
        <div class="kpi-value" style="color: var(--color-warning);">3</div>
      </div>
    </div>
    
    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Próximos Vencimentos</h3>
      </div>
      <div class="card-body">
        <div class="grid grid-3">
          <div class="card" style="border-left: 4px solid var(--color-warning);">
            <div class="card-body">
              <div style="font-weight: 600; margin-bottom: 8px;">ABC-1234 - Troca de Óleo</div>
              <p class="text-secondary" style="font-size: 13px;">Vence em 3 dias</p>
              <button class="btn btn-primary btn-sm" style="margin-top: 12px;">Agendar</button>
            </div>
          </div>
          <div class="card" style="border-left: 4px solid var(--color-warning);">
            <div class="card-body">
              <div style="font-weight: 600; margin-bottom: 8px;">DEF-5678 - Revisão Pneus</div>
              <p class="text-secondary" style="font-size: 13px;">Vence em 5 dias</p>
              <button class="btn btn-primary btn-sm" style="margin-top: 12px;">Agendar</button>
            </div>
          </div>
          <div class="card" style="border-left: 4px solid var(--color-error);">
            <div class="card-body">
              <div style="font-weight: 600; margin-bottom: 8px;">GHI-9012 - IPVA</div>
              <p class="text-secondary" style="font-size: 13px;">Vence hoje!</p>
              <button class="btn btn-primary btn-sm" style="margin-top: 12px;">Pagar</button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Histórico de Manutenções</h3>
        <button class="btn btn-primary btn-sm">Nova Manutenção</button>
      </div>
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Data</th>
              <th>Veículo</th>
              <th>Tipo</th>
              <th>Oficina</th>
              <th>Valor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-mono">10/08/2026</td>
              <td class="font-mono">ABC-1234</td>
              <td>Troca de Óleo</td>
              <td>Oficina Central</td>
              <td class="font-mono">R$ 450,00</td>
              <td><span class="badge badge-success">Concluída</span></td>
            </tr>
            <tr>
              <td class="font-mono">08/08/2026</td>
              <td class="font-mono">DEF-5678</td>
              <td>Revisão Freios</td>
              <td>Oficina Especializada</td>
              <td class="font-mono">R$ 1.200,00</td>
              <td><span class="badge badge-success">Concluída</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  contas: `
    <div class="page-header">
      <h1 class="page-title">Contas a Pagar/Receber</h1>
      <p class="page-description">Gestão financeira de contas</p>
    </div>
    
    <div class="tabs">
      <button class="tab active">Contas a Pagar</button>
      <button class="tab">Contas a Receber</button>
    </div>
    
    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Fluxo Financeiro</h3>
      </div>
      <div class="card-body">
        <div class="chart-placeholder">Gráfico de Linha - Fluxo Financeiro</div>
      </div>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Período:</label>
        <select class="form-select" style="width: auto;">
          <option>Últimos 7 dias</option>
          <option>Últimos 30 dias</option>
          <option>Este mês</option>
          <option>Mês anterior</option>
        </select>
      </div>
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Status:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>Pendente</option>
          <option>Paga</option>
          <option>Atrasada</option>
        </select>
      </div>
      <button class="btn btn-primary">Nova Conta</button>
    </div>
    
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Descrição</th>
              <th>Fornecedor/Cliente</th>
              <th>Vencimento</th>
              <th>Valor</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-mono">#CP001</td>
              <td>Combustível</td>
              <td>Petrobras</td>
              <td class="font-mono">15/08/2026</td>
              <td class="font-mono">R$ 12.345,67</td>
              <td><span class="badge badge-warning">Pendente</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td class="font-mono">#CP002</td>
              <td>Manutenção</td>
              <td>Oficina Central</td>
              <td class="font-mono">20/08/2026</td>
              <td class="font-mono">R$ 3.456,78</td>
              <td><span class="badge badge-warning">Pendente</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td class="font-mono">#CR001</td>
              <td>Frete - Viagem #V001</td>
              <td>Empresa ABC Ltda</td>
              <td class="font-mono">10/08/2026</td>
              <td class="font-mono">R$ 45.678,90</td>
              <td><span class="badge badge-success">Recebida</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <img src="assets/icons/view.svg" alt="View" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  relatorios: `
    <div class="page-header">
      <h1 class="page-title">Relatórios</h1>
      <p class="page-description">Central de relatórios e análises</p>
    </div>
    
    <div class="tabs">
      <button class="tab active">Resumo</button>
      <button class="tab">Clientes</button>
      <button class="tab">Viagens</button>
      <button class="tab">Custos</button>
      <button class="tab">Contas</button>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Período:</label>
        <select class="form-select" style="width: auto;">
          <option>Últimos 7 dias</option>
          <option>Últimos 30 dias</option>
          <option>Este mês</option>
          <option>Mês anterior</option>
          <option>Personalizado</option>
        </select>
      </div>
      <button class="btn btn-outline">
        <img src="assets/icons/export.svg" alt="Exportar" width="16" height="16">
        Exportar PDF
      </button>
    </div>
    
    <div class="grid grid-2" style="margin-bottom: 24px;">
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Resumo Executivo</h3>
        </div>
        <div class="card-body">
          <div style="margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Faturamento Total</span>
              <span class="font-mono" style="font-weight: 600;">R$ 1.234.567</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Custos Totais</span>
              <span class="font-mono" style="font-weight: 600;">R$ 456.789</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
              <span class="text-secondary">Lucro Líquido</span>
              <span class="font-mono" style="font-weight: 600; color: var(--color-success);">R$ 777.778</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span class="text-secondary">Margem de Lucro</span>
              <span class="font-mono" style="font-weight: 600;">63.1%</span>
            </div>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Distribuição por Categoria</h3>
        </div>
        <div class="card-body">
          <div class="chart-placeholder">Gráfico de Pizza</div>
        </div>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Detalhamento por Período</h3>
      </div>
      <div class="card-body">
        <div class="chart-placeholder">Gráfico de Barras - Detalhamento</div>
      </div>
    </div>
  `,
  
  funcionarios: `
    <div class="page-header">
      <h1 class="page-title">Funcionários</h1>
      <p class="page-description">Gestão da equipe e folha de pagamento</p>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 24px;">
      <div class="kpi-card">
        <div class="kpi-label">Total de Funcionários</div>
        <div class="kpi-value">56</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Folha (Mês)</div>
        <div class="kpi-value">R$ 234.567</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Horas Extras</div>
        <div class="kpi-value">450h</div>
      </div>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Departamento:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>Operacional</option>
          <option>Administrativo</option>
          <option>Manutenção</option>
        </select>
      </div>
      <button class="btn btn-primary">Novo Funcionário</button>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 24px;">
      <div class="card">
        <div class="card-body" style="text-align: center;">
          <div style="width: 64px; height: 64px; border-radius: var(--radius-full); background: var(--color-primary); color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 600; margin: 0 auto 16px;">JS</div>
          <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">João Silva</h3>
          <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Motorista</p>
          <p class="text-tertiary" style="font-size: 12px;">Operacional</p>
          <div class="actions" style="justify-content: center; margin-top: 16px;">
            <button class="btn btn-outline btn-sm">Ver Detalhes</button>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-body" style="text-align: center;">
          <div style="width: 64px; height: 64px; border-radius: var(--radius-full); background: var(--color-accent-1); color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 600; margin: 0 auto 16px;">MS</div>
          <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">Maria Santos</h3>
          <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Motorista</p>
          <p class="text-tertiary" style="font-size: 12px;">Operacional</p>
          <div class="actions" style="justify-content: center; margin-top: 16px;">
            <button class="btn btn-outline btn-sm">Ver Detalhes</button>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-body" style="text-align: center;">
          <div style="width: 64px; height: 64px; border-radius: var(--radius-full); background: var(--color-accent-2); color: white; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 600; margin: 0 auto 16px;">CO</div>
          <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">Carlos Oliveira</h3>
          <p class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Motorista</p>
          <p class="text-tertiary" style="font-size: 12px;">Operacional</p>
          <div class="actions" style="justify-content: center; margin-top: 16px;">
            <button class="btn btn-outline btn-sm">Ver Detalhes</button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Cargo</th>
              <th>Departamento</th>
              <th>Salário</th>
              <th>Horas Extras</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>João Silva</td>
              <td>Motorista</td>
              <td>Operacional</td>
              <td class="font-mono">R$ 4.500,00</td>
              <td class="font-mono">45h</td>
              <td><span class="badge badge-success">Ativo</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Maria Santos</td>
              <td>Motorista</td>
              <td>Operacional</td>
              <td class="font-mono">R$ 4.500,00</td>
              <td class="font-mono">32h</td>
              <td><span class="badge badge-success">Ativo</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  usuarios: `
    <div class="page-header">
      <h1 class="page-title">Gerenciar Usuários</h1>
      <p class="page-description">Controle de acesso e permissões do sistema</p>
    </div>
    
    <div class="filters">
      <button class="btn btn-primary">Novo Usuário</button>
    </div>
    
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Email</th>
              <th>Função</th>
              <th>Permissões</th>
              <th>Último Acesso</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>João Silva</td>
              <td class="font-mono">joao@cwtransportadora.com.br</td>
              <td>Administrador</td>
              <td>Total</td>
              <td class="font-mono">13/08/2026 14:30</td>
              <td><span class="badge badge-success">Ativo</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Remover">
                    <img src="assets/icons/delete.svg" alt="Delete" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Maria Santos</td>
              <td class="font-mono">maria@cwtransportadora.com.br</td>
              <td>Operador</td>
              <td>Operacional</td>
              <td class="font-mono">13/08/2026 10:15</td>
              <td><span class="badge badge-success">Ativo</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Remover">
                    <img src="assets/icons/delete.svg" alt="Delete" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Carlos Oliveira</td>
              <td class="font-mono">carlos@cwtransportadora.com.br</td>
              <td>Motorista</td>
              <td>Visualização</td>
              <td class="font-mono">12/08/2026 16:45</td>
              <td><span class="badge badge-warning">Inativo</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Editar">
                    <img src="assets/icons/edit.svg" alt="Edit" width="16" height="16">
                  </button>
                  <button class="icon-button btn-sm" title="Remover">
                    <img src="assets/icons/delete.svg" alt="Delete" width="16" height="16">
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  auditoria: `
    <div class="page-header">
      <h1 class="page-title">Auditoria</h1>
      <p class="page-description">Log de ações e histórico do sistema</p>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Tipo de Ação:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>Criação</option>
          <option>Edição</option>
          <option>Exclusão</option>
          <option>Login</option>
        </select>
      </div>
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Usuário:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>João Silva</option>
          <option>Maria Santos</option>
        </select>
      </div>
      <button class="btn btn-outline">
        <img src="assets/icons/export.svg" alt="Exportar" width="16" height="16">
        Exportar CSV
      </button>
    </div>
    
    <div class="card">
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Data/Hora</th>
              <th>Usuário</th>
              <th>Ação</th>
              <th>Módulo</th>
              <th>Detalhes</th>
              <th>IP</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-mono">13/08/2026 14:30:15</td>
              <td>João Silva</td>
              <td><span class="badge badge-info">Criação</span></td>
              <td>Viagens</td>
              <td>Criou viagem #V001</td>
              <td class="font-mono">192.168.1.100</td>
            </tr>
            <tr>
              <td class="font-mono">13/08/2026 14:25:42</td>
              <td>Maria Santos</td>
              <td><span class="badge badge-warning">Edição</span></td>
              <td>Notas</td>
              <td>Editou nota NF-001234</td>
              <td class="font-mono">192.168.1.101</td>
            </tr>
            <tr>
              <td class="font-mono">13/08/2026 14:20:10</td>
              <td>João Silva</td>
              <td><span class="badge badge-success">Login</span></td>
              <td>Sistema</td>
              <td>Login realizado com sucesso</td>
              <td class="font-mono">192.168.1.100</td>
            </tr>
            <tr>
              <td class="font-mono">13/08/2026 14:15:33</td>
              <td>Carlos Oliveira</td>
              <td><span class="badge badge-error">Exclusão</span></td>
              <td>Notas</td>
              <td>Excluiu nota NF-001230</td>
              <td class="font-mono">192.168.1.102</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  
  versoes: `
    <div class="page-header">
      <h1 class="page-title">Histórico de Versões</h1>
      <p class="page-description">Timeline de atualizações e releases</p>
    </div>
    
    <div class="card">
      <div class="card-body">
        <div style="position: relative; padding-left: 32px;">
          <div style="position: absolute; left: 8px; top: 0; bottom: 0; width: 2px; background: var(--color-border);"></div>
          
          <div style="position: relative; margin-bottom: 32px;">
            <div style="position: absolute; left: -24px; width: 12px; height: 12px; border-radius: 50%; background: var(--color-primary);"></div>
            <div style="background: var(--color-surface); padding: 16px; border-radius: var(--radius-md);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 16px; font-weight: 600;">Versão 8.0</h3>
                <span class="font-mono text-tertiary" style="font-size: 12px;">13/08/2026</span>
              </div>
              <p class="text-secondary" style="font-size: 14px; margin-bottom: 8px;">Redesign completo do sistema com nova interface Enterprise SaaS Modern</p>
              <ul style="font-size: 13px; color: var(--color-text-secondary); padding-left: 20px;">
                <li>Novo design system com paleta Professional Blue</li>
                <li>Interface responsiva com suporte a dark mode</li>
                <li>17 telas redesenhadas com componentes modernos</li>
                <li>Melhorias de acessibilidade e usabilidade</li>
              </ul>
            </div>
          </div>
          
          <div style="position: relative; margin-bottom: 32px;">
            <div style="position: absolute; left: -24px; width: 12px; height: 12px; border-radius: 50%; background: var(--color-text-tertiary);"></div>
            <div style="background: var(--color-surface); padding: 16px; border-radius: var(--radius-md);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 16px; font-weight: 600;">Versão 7.5</h3>
                <span class="font-mono text-tertiary" style="font-size: 12px;">01/07/2026</span>
              </div>
              <p class="text-secondary" style="font-size: 14px; margin-bottom: 8px;">Atualizações de funcionalidades e correções de bugs</p>
              <ul style="font-size: 13px; color: var(--color-text-secondary); padding-left: 20px;">
                <li>Novo módulo de relatórios avançados</li>
                <li>Integração com API de pedágio</li>
                <li>Correções de performance</li>
              </ul>
            </div>
          </div>
          
          <div style="position: relative;">
            <div style="position: absolute; left: -24px; width: 12px; height: 12px; border-radius: 50%; background: var(--color-text-tertiary);"></div>
            <div style="background: var(--color-surface); padding: 16px; border-radius: var(--radius-md);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h3 style="font-size: 16px; font-weight: 600;">Versão 7.0</h3>
                <span class="font-mono text-tertiary" style="font-size: 12px;">15/05/2026</span>
              </div>
              <p class="text-secondary" style="font-size: 14px; margin-bottom: 8px;">Lançamento do módulo de controle de combustível</p>
              <ul style="font-size: 13px; color: var(--color-text-secondary); padding-left: 20px;">
                <li>Módulo de controle de combustível</li>
                <li>Gráficos de consumo</li>
                <li>Alertas de manutenção</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  
  configuracoes: `
    <div class="page-header">
      <h1 class="page-title">Configurações</h1>
      <p class="page-description">Configurações do sistema e da empresa</p>
    </div>
    
    <div class="tabs">
      <button class="tab active">Empresa</button>
      <button class="tab">Metas</button>
      <button class="tab">Sistema</button>
      <button class="tab">Tema</button>
    </div>
    
    <div class="card" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Dados da Empresa</h3>
      </div>
      <div class="card-body">
        <form>
          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">Nome da Empresa</label>
              <input type="text" class="form-input" value="CW Transportadora Ltda">
            </div>
            <div class="form-group">
              <label class="form-label">CNPJ</label>
              <input type="text" class="form-input" value="00.000.000/0001-00">
            </div>
          </div>
          
          <div class="grid grid-2">
            <div class="form-group">
              <label class="form-label">Telefone</label>
              <input type="text" class="form-input" value="(11) 1234-5678">
            </div>
            <div class="form-group">
              <label class="form-label">Email</label>
              <input type="email" class="form-input" value="contato@cwtransportadora.com.br">
            </div>
          </div>
          
          <div class="form-group">
            <label class="form-label">Endereço</label>
            <input type="text" class="form-input" value="Rua Exemplo, 123 - São Paulo, SP">
          </div>
          
          <div class="actions" style="margin-top: 24px;">
            <button type="submit" class="btn btn-primary">Salvar Alterações</button>
          </div>
        </form>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Preferências de Tema</h3>
      </div>
      <div class="card-body">
        <div class="form-group">
          <label class="form-label">Modo Escuro</label>
          <div style="display: flex; align-items: center; gap: 12px;">
            <input type="checkbox" id="dark-mode-toggle">
            <label for="dark-mode-toggle" style="margin: 0;">Ativar modo escuro</label>
          </div>
        </div>
      </div>
    </div>
  `,
  
  perfil: `
    <div class="page-header">
      <h1 class="page-title">Meu Perfil</h1>
      <p class="page-description">Configurações da sua conta</p>
    </div>
    
    <div class="grid grid-3">
      <div class="card" style="grid-column: span 2;">
        <div class="card-header">
          <h3 class="card-title">Informações Pessoais</h3>
        </div>
        <div class="card-body">
          <form>
            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">Nome</label>
                <input type="text" class="form-input" value="João Silva">
              </div>
              <div class="form-group">
                <label class="form-label">Email</label>
                <input type="email" class="form-input" value="joao@cwtransportadora.com.br">
              </div>
            </div>
            
            <div class="grid grid-2">
              <div class="form-group">
                <label class="form-label">Telefone</label>
                <input type="text" class="form-input" value="(11) 98765-4321">
              </div>
              <div class="form-group">
                <label class="form-label">Cargo</label>
                <input type="text" class="form-input" value="Administrador" disabled>
              </div>
            </div>
            
            <div class="actions" style="margin-top: 24px;">
              <button type="submit" class="btn btn-primary">Salvar Alterações</button>
            </div>
          </form>
        </div>
      </div>
      
      <div class="card">
        <div class="card-body" style="text-align: center;">
          <div style="width: 96px; height: 96px; border-radius: var(--radius-full); background: var(--color-primary); color: white; display: flex; align-items: center; justify-content: center; font-size: 36px; font-weight: 600; margin: 0 auto 16px;">JS</div>
          <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 4px;">João Silva</h3>
          <p class="text-secondary" style="margin-bottom: 16px;">Administrador</p>
          <button class="btn btn-outline btn-sm">Alterar Foto</button>
        </div>
      </div>
    </div>
    
    <div class="card" style="margin-top: 24px;">
      <div class="card-header">
        <h3 class="card-title">Alterar Senha</h3>
      </div>
      <div class="card-body">
        <form>
          <div class="grid grid-3">
            <div class="form-group">
              <label class="form-label">Senha Atual</label>
              <input type="password" class="form-input" placeholder="••••••••">
            </div>
            <div class="form-group">
              <label class="form-label">Nova Senha</label>
              <input type="password" class="form-input" placeholder="••••••••">
            </div>
            <div class="form-group">
              <label class="form-label">Confirmar Senha</label>
              <input type="password" class="form-input" placeholder="••••••••">
            </div>
          </div>
          
          <div class="actions" style="margin-top: 24px;">
            <button type="submit" class="btn btn-primary">Alterar Senha</button>
          </div>
        </form>
      </div>
    </div>
  `
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
  // Load default screen
  loadScreen('dashboard');
  
  // Setup navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      const screen = this.getAttribute('data-screen');
      loadScreen(screen);
      
      // Update active state
      document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
      this.classList.add('active');
    });
  });
  
  // Setup theme toggle
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      document.body.classList.toggle('dark-mode');
    });
  }
});

function loadScreen(screenName) {
  const pageContent = document.getElementById('page-content');
  const currentPage = document.getElementById('current-page');
  
  if (screens[screenName]) {
    pageContent.innerHTML = screens[screenName];
    
    // Update breadcrumb
    const screenTitles = {
      'dashboard': 'Dashboard',
      'notas': 'Notas/Manifestos',
      'nova-operacao': 'Nova Operação',
      'criar-viagem': 'Criar Viagem',
      'viagens': 'Histórico de Viagens',
      'ranking': 'Ranking de Clientes',
      'combustivel': 'Combustível',
      'manutencao': 'Manutenção',
      'contas': 'Contas',
      'relatorios': 'Relatórios',
      'funcionarios': 'Funcionários',
      'usuarios': 'Usuários',
      'auditoria': 'Auditoria',
      'versoes': 'Versões',
      'configuracoes': 'Configurações',
      'perfil': 'Meu Perfil'
    };
    
    if (currentPage) {
      currentPage.textContent = screenTitles[screenName] || screenName;
    }
  }
}
