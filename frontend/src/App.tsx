import Layout from './components/Layout'
import TasksPage from './pages/TasksPage'
import TodayPlanPage from './pages/TodayPlanPage'

const App = () => {
	return (
		<Layout>
			<section className='hero' id='home'>
				<p className='eyebrow'>Flowly</p>
				<h1>Keep priorities clear and your day predictable.</h1>
				<p className='lede'>
					Draft a quick plan, capture tasks, and let the AI time manager keep
					you focused on what matters next.
				</p>
				<div className='cta-row'>
					<a className='button primary' href='#tasks'>
						View tasks
					</a>
					<a className='button ghost' href='#today'>
						Today&apos;s plan
					</a>
				</div>
			</section>

			<TasksPage />
			<TodayPlanPage />
		</Layout>
	)
}

export default App
