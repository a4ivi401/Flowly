import flowlyLogo from './assets/flowly-logo.svg'

const App = () => {
  const features = [
    {
      title: 'AI-розклад без хаосу',
      description:
        'Flowly розподіляє пріоритети, підтягує дедлайни і формує таймбокси за хвилини.',
      tag: 'Пріоритети',
    },
    {
      title: 'Командний ритм',
      description:
        'Синхронізує плани команди, показує навантаження і пропонує вікна для спільних задач.',
      tag: 'Синхронізація',
    },
    {
      title: 'Фокус без мікроменеджменту',
      description:
        'Нагадує про наступний крок, захищає фокусні блоки і залишає простір для гнучкості.',
      tag: 'Фокус',
    },
  ]

  const proofPoints = [
    {
      metric: '18%',
      label: 'менше контекстних переключень на день',
    },
    {
      metric: '2х',
      label: 'швидше формування плану спринту',
    },
    {
      metric: '92%',
      label: 'зустрічей проходять вчасно',
    },
  ]

  const steps = [
    {
      title: 'Задайте цілі',
      copy: 'Фіксуємо квартальні цілі та те, що справді треба встигнути цього тижня.',
    },
    {
      title: 'Побудуйте день',
      copy: 'AI пропонує пріоритети, таймбокси і вікна для команди — ви лишаєте відбиток.',
    },
    {
      title: 'Отримуйте підказки',
      copy: 'Flowly тримає вас у курсі: що далі, що перенести, як не втратити фокус.',
    },
  ]

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <img src={flowlyLogo} alt="Flowly" className="brand-logo" />
          <span className="brand-pill">AI time OS</span>
        </div>
        <nav className="nav">
          <a href="#features">Можливості</a>
          <a href="#how">Як працює</a>
          <a href="#cta">Демо</a>
        </nav>
        <a className="ghost-button" href="#cta">
          Запросити демо
        </a>
      </header>

      <main className="content">
        <section className="hero" id="home">
          <div className="hero-copy">
            <p className="eyebrow">Нарешті керований день</p>
            <h1>
              Flowly планує, підказує і знімає шум, щоб команда встигала важливе.
            </h1>
            <p className="lede">
              Одна титульна сторінка для вашого робочого ритму: пріоритети, фокусні блоки,
              прозорий календар і AI, який стежить, щоб темп не падав.
            </p>
            <div className="cta-row">
              <a className="primary-button" href="#cta">
                Запросити демо
              </a>
              <a className="link-button" href="#features">
                Дивитися можливості
              </a>
            </div>
            <div className="proof-strip">
              {proofPoints.map((item) => (
                <div className="proof-card" key={item.metric}>
                  <span className="metric">{item.metric}</span>
                  <span className="metric-label">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="hero-card">
            <div className="hero-badge">Візуальний таймлайн</div>
            <div className="timeline">
              <div className="timeline-item focus">
                <div className="time">09:00 - 11:00</div>
                <div className="title">Фокус: продуктова стратегія</div>
                <div className="note">Flowly тримає цей блок без зустрічей</div>
              </div>
              <div className="timeline-item">
                <div className="time">11:30 - 12:00</div>
                <div className="title">Синк з командою</div>
                <div className="note">Авто-підбір часу без перетинів</div>
              </div>
              <div className="timeline-item">
                <div className="time">15:00 - 16:00</div>
                <div className="title">Глибока робота</div>
                <div className="note">AI нагадає за 10 хв до старту</div>
              </div>
            </div>
          </div>
        </section>

        <section className="features" id="features">
          <div className="section-header">
            <p className="eyebrow">Можливості</p>
            <h2>Одна сторінка, щоб тримати курс</h2>
            <p className="muted">
              Забираємо шум таск-трекерів і залишаємо лише головне: пріоритети, час і ясність.
            </p>
          </div>
          <div className="feature-grid">
            {features.map((feature) => (
              <article className="feature-card" key={feature.title}>
                <span className="tag">{feature.tag}</span>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="how" id="how">
          <div className="section-header">
            <p className="eyebrow">Як працює</p>
            <h2>Три кроки до керованого дня</h2>
            <p className="muted">
              Flowly поєднує ваші цілі, календар і ритм команди — без зайвих сторінок.
            </p>
          </div>
          <div className="steps">
            {steps.map((step, index) => (
              <div className="step-card" key={step.title}>
                <div className="step-index">0{index + 1}</div>
                <h3>{step.title}</h3>
                <p>{step.copy}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="cta" id="cta">
          <div className="cta-inner">
            <div>
              <p className="eyebrow">Готові спробувати?</p>
              <h2>Замовте демо Flowly</h2>
              <p className="muted">
                Покажемо, як ми прибираємо хаос з календаря та підтягуємо командний ритм за тиждень.
              </p>
            </div>
            <a className="primary-button" href="mailto:hello@flowly.ai">
              hello@flowly.ai
            </a>
          </div>
        </section>
      </main>

      <footer className="footer">
        <span>Flowly — AI time OS для команд.</span>
        <span>Залишайтесь у фокусі.</span>
      </footer>
    </div>
  )
}

export default App
