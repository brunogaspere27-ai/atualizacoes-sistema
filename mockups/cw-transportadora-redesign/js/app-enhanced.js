// CW Transportadora - Enhanced JavaScript with Real Charts

// Screen content templates with real Chart.js integration
const screens = {
  dashboard: `
    <div class="page-header">
      <h1 class="page-title">Dashboard Executivo</h1>
      <p class="page-description">Visão geral das operações e métricas em tempo real</p>
    </div>
    
    <div class="filters">
      <button class="btn btn-primary btn-sm active">Hoje</button>
      <button class="btn btn-secondary btn-sm">Semana</button>
      <button class="btn btn-secondary btn-sm">Mês</button>
      <button class="btn btn-secondary btn-sm">Ano</button>
      <button class="btn btn-secondary btn-sm">Personalizado</button>
    </div>
    
    <div class="grid grid-6" style="margin-bottom: 32px;">
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <div class="kpi-label">Faturamento Total</div>
        <div class="kpi-value">R$ 1.234.567</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +12.5%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="1" y="3" width="15" height="13"></rect>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
            <circle cx="5.5" cy="18.5" r="2.5"></circle>
            <circle cx="18.5" cy="18.5" r="2.5"></circle>
          </svg>
        </div>
        <div class="kpi-label">Viagens Realizadas</div>
        <div class="kpi-value">847</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +8.3%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Notas Processadas</div>
        <div class="kpi-value">12.456</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +15.2%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <div class="kpi-label">Custos Operacionais</div>
        <div class="kpi-value">R$ 456.789</div>
        <div class="kpi-trend negative">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
            <polyline points="17 18 23 18 23 12"></polyline>
          </svg>
          +3.2%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Lucro Líquido</div>
        <div class="kpi-value">R$ 777.778</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +18.7%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Margem de Lucro</div>
        <div class="kpi-value">63.1%</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +2.4%
        </div>
      </div>
    </div>
    
    <div class="grid grid-6" style="margin-bottom: 32px;">
      <div class="kpi-card">
        <div class="kpi-label">Clientes Ativos</div>
        <div class="kpi-value">234</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +5.1%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Veículos em Operação</div>
        <div class="kpi-value">42</div>
        <div class="kpi-trend negative">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
            <polyline points="17 18 23 18 23 12"></polyline>
          </svg>
          -2
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Motoristas Ativos</div>
        <div class="kpi-value">56</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +3
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Média por Viagem</div>
        <div class="kpi-value">R$ 1.457</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +4.2%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Entregas no Prazo</div>
        <div class="kpi-value">94.5%</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +1.8%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label">Ticket Médio</div>
        <div class="kpi-value">R$ 5.278</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +6.3%
        </div>
      </div>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 32px;">
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Faturamento Mensal</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-faturamento" height="200"></canvas>
        </div>
      </div>
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Viagens por Região</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-regioes" height="200"></canvas>
        </div>
      </div>
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Distribuição de Custos</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-custos" height="200"></canvas>
        </div>
      </div>
    </div>
    
    <div class="grid grid-2">
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Volume de Notas</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-notas" height="200"></canvas>
        </div>
      </div>
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Performance da Frota</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-frota" height="200"></canvas>
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
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
        </svg>
        Aplicar Filtros
      </button>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 24px;">
      <div class="card card-elevated">
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
      <div class="card card-elevated">
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
      <div class="card card-elevated">
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
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
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
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
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
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
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
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
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
      <div class="card card-elevated" style="grid-column: span 2;">
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
      
      <div class="card card-elevated">
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
    
    <div class="card card-elevated" style="margin-bottom: 24px;">
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
    
    <div class="card card-elevated" style="margin-bottom: 24px;">
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
      <div class="card card-elevated">
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
      
      <div class="card card-elevated">
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
      
      <div class="card card-elevated">
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
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="1" y="3" width="15" height="13"></rect>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
            <circle cx="5.5" cy="18.5" r="2.5"></circle>
            <circle cx="18.5" cy="18.5" r="2.5"></circle>
          </svg>
        </div>
        <div class="kpi-label">Total de Viagens</div>
        <div class="kpi-value">847</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Notas Transportadas</div>
        <div class="kpi-value">12.456</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <div class="kpi-label">Frete Total</div>
        <div class="kpi-value">R$ 1.234.567</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
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
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
        </svg>
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
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Finalizar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
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
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
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
      <p class="page-description">Análise de performance por cliente</p>
    </div>
    
    <div class="grid grid-4" style="margin-bottom: 24px;">
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
        </div>
        <div class="kpi-label">Total de Clientes</div>
        <div class="kpi-value">234</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Top Cliente</div>
        <div class="kpi-value">Empresa ABC</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <div class="kpi-label">Média por Cliente</div>
        <div class="kpi-value">R$ 5.278</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
          </svg>
        </div>
        <div class="kpi-label">Ticket Médio</div>
        <div class="kpi-value">R$ 8.456</div>
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
      <button class="btn btn-primary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
        </svg>
        Aplicar Filtros
      </button>
      <button class="btn btn-outline">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
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
              <th>Volume</th>
              <th>Valor</th>
              <th>Média</th>
              <th>Tendência</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><span class="badge badge-primary">1º</span></td>
              <td>Empresa ABC Ltda</td>
              <td class="font-mono">1.234 notas</td>
              <td class="font-mono">R$ 456.789</td>
              <td class="font-mono">R$ 370</td>
              <td><span class="kpi-trend positive">+12.5%</span></td>
            </tr>
            <tr>
              <td><span class="badge badge-secondary">2º</span></td>
              <td>Comércio XYZ</td>
              <td class="font-mono">987 notas</td>
              <td class="font-mono">R$ 345.678</td>
              <td class="font-mono">R$ 350</td>
              <td><span class="kpi-trend positive">+8.3%</span></td>
            </tr>
            <tr>
              <td><span class="badge badge-secondary">3º</span></td>
              <td>Indústria DEF</td>
              <td class="font-mono">756 notas</td>
              <td class="font-mono">R$ 234.567</td>
              <td class="font-mono">R$ 310</td>
              <td><span class="kpi-trend negative">-2.1%</span></td>
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
    
    <div class="grid grid-4" style="margin-bottom: 24px;">
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <div class="kpi-label">Alertas Ativos</div>
        <div class="kpi-value">3</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <div class="kpi-label">Custo Total</div>
        <div class="kpi-value">R$ 45.678</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="1" y="3" width="15" height="13"></rect>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
            <circle cx="5.5" cy="18.5" r="2.5"></circle>
            <circle cx="18.5" cy="18.5" r="2.5"></circle>
          </svg>
        </div>
        <div class="kpi-label">Viagens Realizadas</div>
        <div class="kpi-value">847</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Média por Viagem</div>
        <div class="kpi-value">R$ 54</div>
      </div>
    </div>
    
    <div class="card card-elevated" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Próximos Vencimentos</h3>
      </div>
      <div class="card-body">
        <div class="grid grid-3">
          <div class="card" style="border-left: 4px solid var(--color-error);">
            <div class="card-body">
              <div style="font-weight: 600; margin-bottom: 8px;">ABC-1234 - Revisão</div>
              <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Vence em 2 dias</div>
              <div class="font-mono" style="font-size: 12px;">Km atual: 95.000 / Km limite: 100.000</div>
            </div>
          </div>
          <div class="card" style="border-left: 4px solid var(--color-warning);">
            <div class="card-body">
              <div style="font-weight: 600; margin-bottom: 8px;">DEF-5678 - Troca de Óleo</div>
              <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Vence em 7 dias</div>
              <div class="font-mono" style="font-size: 12px;">Km atual: 45.000 / Km limite: 50.000</div>
            </div>
          </div>
          <div class="card" style="border-left: 4px solid var(--color-success);">
            <div class="card-body">
              <div style="font-weight: 600; margin-bottom: 8px;">GHI-9012 - Pneus</div>
              <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Vence em 15 dias</div>
              <div class="font-mono" style="font-size: 12px;">Km atual: 78.000 / Km limite: 85.000</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Histórico de Manutenções</h3>
        <button class="btn btn-primary btn-sm">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Nova Manutenção
        </button>
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
              <td>ABC-1234</td>
              <td>Revisão Completa</td>
              <td>Oficina Mecânica Central</td>
              <td class="font-mono">R$ 2.345,67</td>
              <td><span class="badge badge-success">Concluída</span></td>
            </tr>
            <tr>
              <td class="font-mono">05/08/2026</td>
              <td>DEF-5678</td>
              <td>Troca de Pneus</td>
              <td>Pneus Brasil</td>
              <td class="font-mono">R$ 4.567,89</td>
              <td><span class="badge badge-success">Concluída</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,

  funcionarios: `
    <div class="page-header">
      <h1 class="page-title">Funcionários</h1>
      <p class="page-description">Gestão de equipe e folha de pagamento</p>
    </div>
    
    <div class="grid grid-4" style="margin-bottom: 24px;">
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
        </div>
        <div class="kpi-label">Total de Funcionários</div>
        <div class="kpi-value">56</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="1" y="3" width="15" height="13"></rect>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
            <circle cx="5.5" cy="18.5" r="2.5"></circle>
            <circle cx="18.5" cy="18.5" r="2.5"></circle>
          </svg>
        </div>
        <div class="kpi-label">Motoristas Ativos</div>
        <div class="kpi-value">42</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <div class="kpi-label">Folha de Pagamento</div>
        <div class="kpi-value">R$ 145.678</div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Horas Extras</div>
        <div class="kpi-value">234h</div>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Equipe</h3>
        <button class="btn btn-primary btn-sm">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Novo Funcionário
        </button>
      </div>
      <div class="card-body">
        <div class="grid grid-3">
          <div class="card card-elevated">
            <div class="card-body" style="text-align: center;">
              <div class="user-avatar" style="width: 64px; height: 64px; font-size: 24px; margin: 0 auto 16px;">JS</div>
              <div style="font-weight: 600; margin-bottom: 4px;">João Silva</div>
              <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Motorista</div>
              <div class="font-mono" style="font-size: 12px;">R$ 4.500/mês</div>
            </div>
          </div>
          <div class="card card-elevated">
            <div class="card-body" style="text-align: center;">
              <div class="user-avatar" style="width: 64px; height: 64px; font-size: 24px; margin: 0 auto 16px;">MS</div>
              <div style="font-weight: 600; margin-bottom: 4px;">Maria Santos</div>
              <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Motorista</div>
              <div class="font-mono" style="font-size: 12px;">R$ 4.200/mês</div>
            </div>
          </div>
          <div class="card card-elevated">
            <div class="card-body" style="text-align: center;">
              <div class="user-avatar" style="width: 64px; height: 64px; font-size: 24px; margin: 0 auto 16px;">CO</div>
              <div style="font-weight: 600; margin-bottom: 4px;">Carlos Oliveira</div>
              <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">Motorista</div>
              <div class="font-mono" style="font-size: 12px;">R$ 4.800/mês</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,

  usuarios: `
    <div class="page-header">
      <h1 class="page-title">Gerenciar Usuários</h1>
      <p class="page-description">Gestão de acessos e permissões</p>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Usuários do Sistema</h3>
        <button class="btn btn-primary btn-sm">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Novo Usuário
        </button>
      </div>
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Nome</th>
              <th>Email</th>
              <th>Função</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>João Silva</td>
              <td class="font-mono">joao@cwtransportadora.com.br</td>
              <td>Administrador</td>
              <td><span class="badge badge-success">Ativo</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Remover">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Maria Santos</td>
              <td class="font-mono">maria@cwtransportadora.com.br</td>
              <td>Operador</td>
              <td><span class="badge badge-success">Ativo</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Remover">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
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
      <p class="page-description">Registro de ações do sistema</p>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label style="font-size: 14px; font-weight: 500; color: var(--color-text-primary);">Tipo de Ação:</label>
        <select class="form-select" style="width: auto;">
          <option>Todos</option>
          <option>Login</option>
          <option>Alteração</option>
          <option>Exclusão</option>
        </select>
      </div>
      <button class="btn btn-primary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
        </svg>
        Aplicar Filtros
      </button>
      <button class="btn btn-outline">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
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
              <th>Detalhes</th>
              <th>IP</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-mono">13/08/2026 10:30</td>
              <td>João Silva</td>
              <td><span class="badge badge-success">Login</span></td>
              <td>Login realizado com sucesso</td>
              <td class="font-mono">192.168.1.100</td>
            </tr>
            <tr>
              <td class="font-mono">13/08/2026 10:25</td>
              <td>Maria Santos</td>
              <td><span class="badge badge-info">Alteração</span></td>
              <td>Alterou viagem #V1234</td>
              <td class="font-mono">192.168.1.105</td>
            </tr>
            <tr>
              <td class="font-mono">13/08/2026 10:20</td>
              <td>Carlos Oliveira</td>
              <td><span class="badge badge-error">Tentativa Falha</span></td>
              <td>Senha incorreta</td>
              <td class="font-mono">192.168.1.110</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,

  versoes: `
    <div class="page-header">
      <h1 class="page-title">Histórico de Versões</h1>
      <p class="page-description">Informações de atualizações do sistema</p>
    </div>
    
    <div class="card">
      <div class="card-body">
        <div style="position: relative; padding-left: 32px;">
          <div style="position: absolute; left: 8px; top: 0; bottom: 0; width: 2px; background: var(--color-border);"></div>
          
          <div style="position: relative; padding-bottom: 32px;">
            <div style="position: absolute; left: -26px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: var(--color-primary);"></div>
            <div style="font-weight: 600; margin-bottom: 4px;">Versão 2.5.0</div>
            <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">13/08/2026</div>
            <div style="font-size: 14px;">
              <ul style="margin: 0; padding-left: 20px;">
                <li>Novos gráficos interativos no Dashboard</li>
                <li>Melhorias no design de cards KPI</li>
                <li>Otimização de performance</li>
              </ul>
            </div>
          </div>
          
          <div style="position: relative; padding-bottom: 32px;">
            <div style="position: absolute; left: -26px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: var(--color-secondary);"></div>
            <div style="font-weight: 600; margin-bottom: 4px;">Versão 2.4.0</div>
            <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">01/08/2026</div>
            <div style="font-size: 14px;">
              <ul style="margin: 0; padding-left: 20px;">
                <li>Novo módulo de relatórios</li>
                <li>Integração com sistema de pagamentos</li>
                <li>Correção de bugs</li>
              </ul>
            </div>
          </div>
          
          <div style="position: relative;">
            <div style="position: absolute; left: -26px; top: 0; width: 12px; height: 12px; border-radius: 50%; background: var(--color-success);"></div>
            <div style="font-weight: 600; margin-bottom: 4px;">Versão 2.3.0</div>
            <div class="text-secondary" style="font-size: 13px; margin-bottom: 8px;">15/07/2026</div>
            <div style="font-size: 14px;">
              <ul style="margin: 0; padding-left: 20px;">
                <li>Redesign completo da interface</li>
                <li>Novo design system NEXUS v8.0</li>
                <li>Migração para PySide6</li>
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
    
    <div class="grid grid-2">
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Dados da Empresa</h3>
        </div>
        <div class="card-body">
          <form>
            <div class="form-group">
              <label class="form-label">Nome da Empresa</label>
              <input type="text" class="form-input" value="CW Transportadora">
            </div>
            <div class="form-group">
              <label class="form-label">CNPJ</label>
              <input type="text" class="form-input" value="00.000.000/0001-00">
            </div>
            <div class="form-group">
              <label class="form-label">Cidade</label>
              <input type="text" class="form-input" value="Cascavel, PR">
            </div>
            <button type="submit" class="btn btn-primary">Salvar</button>
          </form>
        </div>
      </div>
      
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Preferências do Sistema</h3>
        </div>
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">Tema</label>
            <select class="form-select">
              <option>Claro</option>
              <option>Escuro</option>
              <option>Automático</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Idioma</label>
            <select class="form-select">
              <option>Português (Brasil)</option>
              <option>Inglês</option>
              <option>Espanhol</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Pasta de Relatórios</label>
            <input type="text" class="form-input" value="C:\Relatorios\CW">
          </div>
          <button type="submit" class="btn btn-primary">Salvar</button>
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
      <div class="card card-elevated" style="grid-column: span 2;">
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
            <div class="form-group">
              <label class="form-label">Cargo</label>
              <input type="text" class="form-input" value="Administrador">
            </div>
            <button type="submit" class="btn btn-primary">Atualizar</button>
          </form>
        </div>
      </div>
      
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Avatar</h3>
        </div>
        <div class="card-body" style="text-align: center;">
          <div class="user-avatar" style="width: 96px; height: 96px; font-size: 36px; margin: 0 auto 16px;">JS</div>
          <button class="btn btn-secondary btn-sm">Alterar Avatar</button>
        </div>
      </div>
    </div>
    
    <div class="card card-elevated" style="margin-top: 24px;">
      <div class="card-header">
        <h3 class="card-title">Alterar Senha</h3>
      </div>
      <div class="card-body">
        <form>
          <div class="grid grid-3">
            <div class="form-group">
              <label class="form-label">Senha Atual</label>
              <input type="password" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">Nova Senha</label>
              <input type="password" class="form-input">
            </div>
            <div class="form-group">
              <label class="form-label">Confirmar Nova Senha</label>
              <input type="password" class="form-input">
            </div>
          </div>
          <button type="submit" class="btn btn-primary">Alterar Senha</button>
        </form>
      </div>
    </div>
  `,

  combustivel: `
    <div class="page-header">
      <h1 class="page-title">Controle de Combustível</h1>
      <p class="page-description">Monitoramento de consumo e abastecimentos</p>
    </div>
    
    <div class="grid grid-4" style="margin-bottom: 24px;">
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M3 22v-8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8"></path>
            <path d="M18 10V6a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v4"></path>
            <line x1="12" y1="2" x2="12" y2="22"></line>
          </svg>
        </div>
        <div class="kpi-label">Consumo Médio</div>
        <div class="kpi-value">8.9 km/L</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +0.4
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <div class="kpi-label">Total Gasto</div>
        <div class="kpi-value">R$ 45.678</div>
        <div class="kpi-trend negative">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
            <polyline points="17 18 23 18 23 12"></polyline>
          </svg>
          +5.2%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Litros Abastecidos</div>
        <div class="kpi-value">5.234 L</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +8.1%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <rect x="1" y="3" width="15" height="13"></rect>
            <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"></polygon>
            <circle cx="5.5" cy="18.5" r="2.5"></circle>
            <circle cx="18.5" cy="18.5" r="2.5"></circle>
          </svg>
        </div>
        <div class="kpi-label">Km Rodados</div>
        <div class="kpi-value">45.678 km</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +12.3%
        </div>
      </div>
    </div>
    
    <div class="grid grid-2" style="margin-bottom: 24px;">
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Consumo ao Longo do Tempo</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-consumo-tempo" height="200"></canvas>
        </div>
      </div>
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Consumo por Veículo</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-consumo-veiculo" height="200"></canvas>
        </div>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Histórico de Abastecimentos</h3>
        <button class="btn btn-primary btn-sm">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Novo Abastecimento
        </button>
      </div>
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
              <th>Km/L</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="font-mono">13/08/2026</td>
              <td>ABC-1234</td>
              <td>João Silva</td>
              <td class="font-mono">150 L</td>
              <td class="font-mono">R$ 5,89</td>
              <td class="font-mono">R$ 883,50</td>
              <td class="font-mono">8,5</td>
            </tr>
            <tr>
              <td class="font-mono">12/08/2026</td>
              <td>DEF-5678</td>
              <td>Maria Santos</td>
              <td class="font-mono">180 L</td>
              <td class="font-mono">R$ 5,92</td>
              <td class="font-mono">R$ 1.065,60</td>
              <td class="font-mono">9,1</td>
            </tr>
            <tr>
              <td class="font-mono">11/08/2026</td>
              <td>GHI-9012</td>
              <td>Carlos Oliveira</td>
              <td class="font-mono">165 L</td>
              <td class="font-mono">R$ 5,87</td>
              <td class="font-mono">R$ 968,55</td>
              <td class="font-mono">8,8</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,

  contas: `
    <div class="page-header">
      <h1 class="page-title">Contas a Pagar/Receber</h1>
      <p class="page-description">Gestão financeira e fluxo de caixa</p>
    </div>
    
    <div class="tabs">
      <button class="tab active">Contas a Pagar</button>
      <button class="tab">Contas a Receber</button>
      <button class="tab">Fluxo de Caixa</button>
    </div>
    
    <div class="grid grid-4" style="margin-bottom: 24px;">
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <line x1="12" y1="1" x2="12" y2="23"></line>
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <div class="kpi-label">A Pagar</div>
        <div class="kpi-value">R$ 45.678</div>
        <div class="kpi-trend negative">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
            <polyline points="17 18 23 18 23 12"></polyline>
          </svg>
          +8.2%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
        </div>
        <div class="kpi-label">A Receber</div>
        <div class="kpi-value">R$ 123.456</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +15.3%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
          </svg>
        </div>
        <div class="kpi-label">Saldo Líquido</div>
        <div class="kpi-value">R$ 77.778</div>
        <div class="kpi-trend positive">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
          +22.1%
        </div>
      </div>
      <div class="kpi-card kpi-card-gradient">
        <div class="kpi-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <polyline points="12 6 12 12 16 14"></polyline>
          </svg>
        </div>
        <div class="kpi-label">Vencidos</div>
        <div class="kpi-value">R$ 12.345</div>
        <div class="kpi-trend negative">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
            <polyline points="17 18 23 18 23 12"></polyline>
          </svg>
          +3.5%
        </div>
      </div>
    </div>
    
    <div class="card card-elevated" style="margin-bottom: 24px;">
      <div class="card-header">
        <h3 class="card-title">Fluxo de Caixa</h3>
        <div class="card-actions">
          <button class="icon-button btn-sm">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="1"></circle>
              <circle cx="19" cy="12" r="1"></circle>
              <circle cx="5" cy="12" r="1"></circle>
            </svg>
          </button>
        </div>
      </div>
      <div class="card-body">
        <canvas id="chart-fluxo-caixa" height="200"></canvas>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Contas a Pagar</h3>
        <button class="btn btn-primary btn-sm">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Nova Conta
        </button>
      </div>
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Fornecedor</th>
              <th>Descrição</th>
              <th>Vencimento</th>
              <th>Valor</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Petrobras</td>
              <td>Combustível</td>
              <td class="font-mono">15/08/2026</td>
              <td class="font-mono">R$ 5.678,90</td>
              <td><span class="badge badge-warning">A vencer</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Pagar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Oficina Mecânica</td>
              <td>Manutenção</td>
              <td class="font-mono">10/08/2026</td>
              <td class="font-mono">R$ 2.345,67</td>
              <td><span class="badge badge-error">Vencida</span></td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Pagar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Editar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
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
      <h1 class="page-title">Relatórios Gerenciais</h1>
      <p class="page-description">Análise e exportação de relatórios</p>
    </div>
    
    <div class="tabs">
      <button class="tab active">Resumo</button>
      <button class="tab">Clientes</button>
      <button class="tab">Viagens</button>
      <button class="tab">Custos</button>
      <button class="tab">Contas</button>
    </div>
    
    <div class="grid grid-3" style="margin-bottom: 24px;">
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Receita vs Despesa</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-receita-despesa" height="200"></canvas>
        </div>
      </div>
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Performance por Cliente</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-clientes-performance" height="200"></canvas>
        </div>
      </div>
      <div class="card card-elevated">
        <div class="card-header">
          <h3 class="card-title">Custos por Categoria</h3>
          <div class="card-actions">
            <button class="icon-button btn-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="1"></circle>
                <circle cx="19" cy="12" r="1"></circle>
                <circle cx="5" cy="12" r="1"></circle>
              </svg>
            </button>
          </div>
        </div>
        <div class="card-body">
          <canvas id="chart-custos-categoria" height="200"></canvas>
        </div>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3 class="card-title">Relatórios Disponíveis</h3>
        <button class="btn btn-primary btn-sm">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Exportar Tudo
        </button>
      </div>
      <div class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>Relatório</th>
              <th>Período</th>
              <th>Gerado em</th>
              <th>Tamanho</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Resumo Financeiro</td>
              <td>Agosto 2026</td>
              <td class="font-mono">13/08/2026 10:30</td>
              <td class="font-mono">2.5 MB</td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Download">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="7 10 12 15 17 10"></polyline>
                      <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
            <tr>
              <td>Análise de Clientes</td>
              <td>Agosto 2026</td>
              <td class="font-mono">12/08/2026 15:45</td>
              <td class="font-mono">1.8 MB</td>
              <td>
                <div class="actions">
                  <button class="icon-button btn-sm" title="Visualizar">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button class="icon-button btn-sm" title="Download">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="7 10 12 15 17 10"></polyline>
                      <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
};

// Keep other screens from original app.js
// (For brevity, I'm keeping the rest of the screens similar but will enhance them progressively)

// Initialize Charts
function initCharts() {
  const chartColors = {
    primary: '#0F62FE',
    primaryLight: '#4589FF',
    secondary: '#8A3FFC',
    success: '#198038',
    warning: '#F1C21B',
    error: '#DA1E28',
    info: '#009D9A',
    gradient1: 'rgba(15, 98, 254, 0.8)',
    gradient2: 'rgba(138, 63, 252, 0.8)',
    gradient3: 'rgba(0, 157, 154, 0.8)',
  };

  // Initialize dashboard charts
  initDashboardCharts(chartColors);
  
  // Initialize other screen charts if they exist
  initCombustivelCharts(chartColors);
  initContasCharts(chartColors);
  initRelatoriosCharts(chartColors);
}

function initDashboardCharts(chartColors) {

  // Faturamento Mensal - Line Chart
  const ctxFaturamento = document.getElementById('chart-faturamento');
  if (ctxFaturamento) {
    new Chart(ctxFaturamento, {
      type: 'line',
      data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
        datasets: [{
          label: 'Faturamento 2024',
          data: [850000, 920000, 880000, 950000, 1020000, 1100000, 1050000, 1150000, 1200000, 1180000, 1250000, 1234567],
          borderColor: chartColors.primary,
          backgroundColor: (context) => {
            const ctx = context.chart.ctx;
            const gradient = ctx.createLinearGradient(0, 0, 0, 200);
            gradient.addColorStop(0, 'rgba(15, 98, 254, 0.3)');
            gradient.addColorStop(1, 'rgba(15, 98, 254, 0.0)');
            return gradient;
          },
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: chartColors.primary,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
        }, {
          label: 'Faturamento 2023',
          data: [720000, 780000, 750000, 820000, 890000, 950000, 920000, 980000, 1020000, 1000000, 1080000, 1050000],
          borderColor: chartColors.secondary,
          backgroundColor: 'transparent',
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
          tension: 0.4,
          pointRadius: 3,
          pointHoverRadius: 5,
          pointBackgroundColor: chartColors.secondary,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                family: 'Inter',
                size: 12
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
            displayColors: true,
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return 'R$ ' + (value / 1000) + 'k';
              },
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            ticks: {
              font: { family: 'Inter', size: 11 }
            },
            grid: {
              display: false
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    });
  }

  // Viagens por Região - Bar Chart
  const ctxRegioes = document.getElementById('chart-regioes');
  if (ctxRegioes) {
    new Chart(ctxRegioes, {
      type: 'bar',
      data: {
        labels: ['São Paulo', 'Paraná', 'Santa Catarina', 'Rio Grande do Sul', 'Minas Gerais', 'Outros'],
        datasets: [{
          label: 'Viagens',
          data: [245, 198, 156, 134, 89, 25],
          backgroundColor: [
            chartColors.gradient1,
            chartColors.gradient2,
            chartColors.gradient3,
            'rgba(25, 128, 56, 0.8)',
            'rgba(241, 194, 27, 0.8)',
            'rgba(218, 30, 40, 0.8)'
          ],
          borderColor: [
            chartColors.primary,
            chartColors.secondary,
            chartColors.info,
            chartColors.success,
            chartColors.warning,
            chartColors.error
          ],
          borderWidth: 2,
          borderRadius: 8,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            ticks: {
              font: { family: 'Inter', size: 10 },
              maxRotation: 45,
              minRotation: 45
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
  }

  // Distribuição de Custos - Doughnut Chart
  const ctxCustos = document.getElementById('chart-custos');
  if (ctxCustos) {
    new Chart(ctxCustos, {
      type: 'doughnut',
      data: {
        labels: ['Combustível', 'Pedágio', 'Manutenção', 'Salários', 'Outros'],
        datasets: [{
          data: [35, 20, 15, 25, 5],
          backgroundColor: [
            chartColors.primary,
            chartColors.secondary,
            chartColors.info,
            chartColors.success,
            chartColors.warning
          ],
          borderColor: '#ffffff',
          borderWidth: 3,
          hoverOffset: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
            labels: {
              usePointStyle: true,
              padding: 15,
              font: {
                family: 'Inter',
                size: 11
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                return context.label + ': ' + context.parsed + '%';
              }
            }
          }
        },
        cutout: '65%'
      }
    });
  }

  // Volume de Notas - Area Chart
  const ctxNotas = document.getElementById('chart-notas');
  if (ctxNotas) {
    new Chart(ctxNotas, {
      type: 'line',
      data: {
        labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
        datasets: [{
          label: 'Notas Processadas',
          data: [1234, 1456, 1389, 1567, 1890, 890, 456],
          borderColor: chartColors.info,
          backgroundColor: (context) => {
            const ctx = context.chart.ctx;
            const gradient = ctx.createLinearGradient(0, 0, 0, 200);
            gradient.addColorStop(0, 'rgba(0, 157, 154, 0.4)');
            gradient.addColorStop(1, 'rgba(0, 157, 154, 0.0)');
            return gradient;
          },
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: chartColors.info,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          x: {
            ticks: {
              font: { family: 'Inter', size: 11 }
            },
            grid: {
              display: false
            }
          }
        }
      }
    });
  }

  // Performance da Frota - Multi-line Chart
  const ctxFrota = document.getElementById('chart-frota');
  if (ctxFrota) {
    new Chart(ctxFrota, {
      type: 'line',
      data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        datasets: [{
          label: 'Eficiência (km/L)',
          data: [8.5, 8.7, 8.6, 8.9, 9.1, 9.0],
          borderColor: chartColors.success,
          backgroundColor: 'transparent',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          yAxisID: 'y',
        }, {
          label: 'Custo por km (R$)',
          data: [2.5, 2.4, 2.45, 2.3, 2.2, 2.25],
          borderColor: chartColors.error,
          backgroundColor: 'transparent',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
          yAxisID: 'y1',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: {
                family: 'Inter',
                size: 12
              }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          y: {
            type: 'linear',
            display: true,
            position: 'left',
            title: {
              display: true,
              text: 'km/L',
              font: { family: 'Inter', size: 11 }
            },
            ticks: {
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: {
              color: 'rgba(0, 0, 0, 0.05)'
            }
          },
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            title: {
              display: true,
              text: 'R$/km',
              font: { family: 'Inter', size: 11 }
            },
            ticks: {
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: {
              drawOnChartArea: false
            }
          },
          x: {
            ticks: {
              font: { family: 'Inter', size: 11 }
            },
            grid: {
              display: false
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        }
      }
    });
  }
}

// Navigation and screen loading
function loadScreen(screenName) {
  const pageContent = document.getElementById('page-content');
  const currentPage = document.getElementById('current-page');
  
  // Update active nav item
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
    if (item.dataset.screen === screenName) {
      item.classList.add('active');
    }
  });
  
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
    'perfil': 'Perfil'
  };
  
  if (currentPage) {
    currentPage.textContent = screenTitles[screenName] || screenName;
  }
  
  // Load screen content
  if (screens[screenName]) {
    pageContent.innerHTML = screens[screenName];
    
    // Initialize charts based on screen
    setTimeout(() => {
      if (screenName === 'dashboard') {
        initCharts();
      } else if (screenName === 'combustivel') {
        initCharts();
      } else if (screenName === 'contas') {
        initCharts();
      } else if (screenName === 'relatorios') {
        initCharts();
      }
    }, 100);
  }
}

// Theme toggle
function initThemeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('dark-mode');
      // Save preference
      const isDark = document.body.classList.contains('dark-mode');
      localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
      document.body.classList.add('dark-mode');
    }
  }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
  // Load initial screen
  loadScreen('dashboard');
  
  // Setup navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const screenName = item.dataset.screen;
      if (screenName) {
        loadScreen(screenName);
      }
    });
  });
  
  // Initialize theme toggle
  initThemeToggle();
  
  // Keyboard shortcut for search
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      const searchInput = document.querySelector('.search-bar input');
      if (searchInput) {
        searchInput.focus();
      }
    }
  });
}

function initCombustivelCharts(chartColors) {
  // Consumo ao Longo do Tempo
  const ctxConsumoTempo = document.getElementById('chart-consumo-tempo');
  if (ctxConsumoTempo) {
    new Chart(ctxConsumoTempo, {
      type: 'line',
      data: {
        labels: ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
        datasets: [{
          label: 'Consumo (km/L)',
          data: [8.5, 8.7, 8.6, 8.9],
          borderColor: chartColors.success,
          backgroundColor: (context) => {
            const ctx = context.chart.ctx;
            const gradient = ctx.createLinearGradient(0, 0, 0, 200);
            gradient.addColorStop(0, 'rgba(25, 128, 56, 0.3)');
            gradient.addColorStop(1, 'rgba(25, 128, 56, 0.0)');
            return gradient;
          },
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: chartColors.success,
          pointBorderColor: '#fff',
          pointBorderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            min: 8,
            max: 10,
            ticks: {
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            ticks: { font: { family: 'Inter', size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Consumo por Veículo
  const ctxConsumoVeiculo = document.getElementById('chart-consumo-veiculo');
  if (ctxConsumoVeiculo) {
    new Chart(ctxConsumoVeiculo, {
      type: 'bar',
      data: {
        labels: ['ABC-1234', 'DEF-5678', 'GHI-9012', 'JKL-3456', 'MNO-6789'],
        datasets: [{
          label: 'km/L',
          data: [8.5, 9.1, 8.8, 9.3, 8.7],
          backgroundColor: [
            'rgba(15, 98, 254, 0.8)',
            'rgba(25, 128, 56, 0.8)',
            'rgba(138, 63, 252, 0.8)',
            'rgba(0, 157, 154, 0.8)',
            'rgba(241, 194, 27, 0.8)'
          ],
          borderColor: [
            chartColors.primary,
            chartColors.success,
            chartColors.secondary,
            chartColors.info,
            chartColors.warning
          ],
          borderWidth: 2,
          borderRadius: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          y: {
            beginAtZero: false,
            min: 8,
            max: 10,
            ticks: { font: { family: 'JetBrains Mono', size: 11 } },
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            ticks: { font: { family: 'Inter', size: 10 }, maxRotation: 45, minRotation: 45 },
            grid: { display: false }
          }
        }
      }
    });
  }
}

function initContasCharts(chartColors) {
  // Fluxo de Caixa
  const ctxFluxoCaixa = document.getElementById('chart-fluxo-caixa');
  if (ctxFluxoCaixa) {
    new Chart(ctxFluxoCaixa, {
      type: 'bar',
      data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago'],
        datasets: [{
          label: 'Receitas',
          data: [85000, 92000, 88000, 95000, 102000, 110000, 105000, 115000],
          backgroundColor: 'rgba(25, 128, 56, 0.8)',
          borderColor: chartColors.success,
          borderWidth: 2,
          borderRadius: 8,
        }, {
          label: 'Despesas',
          data: [45000, 48000, 46000, 50000, 52000, 55000, 53000, 56000],
          backgroundColor: 'rgba(218, 30, 40, 0.8)',
          borderColor: chartColors.error,
          borderWidth: 2,
          borderRadius: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: { family: 'Inter', size: 12 }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return 'R$ ' + (value / 1000) + 'k';
              },
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            ticks: { font: { family: 'Inter', size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }
}

function initRelatoriosCharts(chartColors) {
  // Receita vs Despesa
  const ctxReceitaDespesa = document.getElementById('chart-receita-despesa');
  if (ctxReceitaDespesa) {
    new Chart(ctxReceitaDespesa, {
      type: 'line',
      data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
        datasets: [{
          label: 'Receita',
          data: [85000, 92000, 88000, 95000, 102000, 110000],
          borderColor: chartColors.success,
          backgroundColor: 'transparent',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
        }, {
          label: 'Despesa',
          data: [45000, 48000, 46000, 50000, 52000, 55000],
          borderColor: chartColors.error,
          backgroundColor: 'transparent',
          borderWidth: 3,
          fill: false,
          tension: 0.4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              usePointStyle: true,
              padding: 20,
              font: { family: 'Inter', size: 12 }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return 'R$ ' + (value / 1000) + 'k';
              },
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            ticks: { font: { family: 'Inter', size: 11 } },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Performance por Cliente
  const ctxClientesPerformance = document.getElementById('chart-clientes-performance');
  if (ctxClientesPerformance) {
    new Chart(ctxClientesPerformance, {
      type: 'bar',
      data: {
        labels: ['Cliente A', 'Cliente B', 'Cliente C', 'Cliente D', 'Cliente E'],
        datasets: [{
          label: 'Faturamento',
          data: [45000, 38000, 32000, 28000, 25000],
          backgroundColor: 'rgba(15, 98, 254, 0.8)',
          borderColor: chartColors.primary,
          borderWidth: 2,
          borderRadius: 8,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return 'R$ ' + (value / 1000) + 'k';
              },
              font: { family: 'JetBrains Mono', size: 11 }
            },
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            ticks: { font: { family: 'Inter', size: 10 }, maxRotation: 45, minRotation: 45 },
            grid: { display: false }
          }
        }
      }
    });
  }

  // Custos por Categoria
  const ctxCustosCategoria = document.getElementById('chart-custos-categoria');
  if (ctxCustosCategoria) {
    new Chart(ctxCustosCategoria, {
      type: 'doughnut',
      data: {
        labels: ['Combustível', 'Manutenção', 'Salários', 'Pedágio', 'Outros'],
        datasets: [{
          data: [35, 20, 25, 12, 8],
          backgroundColor: [
            chartColors.primary,
            chartColors.secondary,
            chartColors.success,
            chartColors.warning,
            chartColors.error
          ],
          borderColor: '#ffffff',
          borderWidth: 3,
          hoverOffset: 10
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'right',
            labels: {
              usePointStyle: true,
              padding: 15,
              font: { family: 'Inter', size: 11 }
            }
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleFont: { family: 'Inter', size: 13 },
            bodyFont: { family: 'JetBrains Mono', size: 12 },
            padding: 12,
            cornerRadius: 8,
            callbacks: {
              label: function(context) {
                return context.label + ': ' + context.parsed + '%';
              }
            }
          }
        },
        cutout: '65%'
      }
    });
  }
});

// Export for external use
window.CWTransportadora = {
  loadScreen,
  initCharts,
  initThemeToggle
};