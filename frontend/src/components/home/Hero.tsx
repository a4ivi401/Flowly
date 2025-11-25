import { Button } from '@/components/ui/button'
import { Link } from 'react-router-dom'
import StatCard from './StatCard'

const Hero = () => {
	return (
		<section className='min-h-screen pt-32 pb-20'>
			<div className='container mx-auto px-6'>
				<div className='grid lg:grid-cols-2 gap-12 items-start'>
					{/* Left Content */}
					<div className='space-y-8'>
						<div className='space-y-6'>
							<p className='text-primary font-semibold uppercase tracking-wide text-sm'>
								Нарешті керований день
							</p>

							<h1 className='text-5xl md:text-6xl font-bold leading-tight text-foreground'>
								Flowly планує, підказує і знімає шум, щоб команда встигала
								важливе.
							</h1>

							<p className='text-lg text-muted-foreground max-w-xl'>
								Професійний асистент вашого робочого ритму: пріоритети, фокусні
								блоки, прозорий календар і AI.
							</p>
						</div>

						<div className='flex flex-wrap gap-4'>
							<Button variant='hero' size='lg' className='text-lg px-8' asChild>
								<Link to='/tasks'>Запросити демо</Link>
							</Button>
							<Button variant='outline' size='lg' className='text-lg px-8'>
								Дивитися можливості
							</Button>
						</div>

						{/* Stats Cards */}
						<div className='grid sm:grid-cols-3 gap-4 pt-8'>
							<StatCard
								percentage='18%'
								description='менше контекстних переключень на день'
							/>
							<StatCard
								percentage='2x'
								description='швидше формування плану спринту'
							/>
							<StatCard
								percentage='92%'
								description='зустрічей проходять вчасно'
							/>
						</div>
					</div>

					{/* Right Content - Timeline */}
					<div className='lg:pt-16'>
						<div className='bg-card/50 backdrop-blur-sm rounded-2xl p-6 border border-border shadow-lg'>
							<h3 className='font-semibold mb-6 text-foreground'>
								Візуальний таймлайн
							</h3>
							<div className='space-y-4'>
								<TimelineItem
									time='09:00 - 11:00'
									title='Фокус: продуктова стратегія'
									description='Flowly тримає цей блок без зустрічей'
								/>
								<TimelineItem
									time='11:30 - 12:00'
									title='Синк з командою'
									description='Авто-підбір часу без перетинів'
								/>
								<TimelineItem
									time='15:00 - 16:00'
									title='Глибока робота'
									description='AI нагадає за 10 хв до старту'
								/>
							</div>
						</div>
					</div>
				</div>
			</div>
		</section>
	)
}

const TimelineItem = ({
	time,
	title,
	description,
}: {
	time: string
	title: string
	description: string
}) => {
	return (
		<div className='bg-secondary/50 rounded-xl p-4 border border-primary/10 hover:border-primary/30 transition-colors'>
			<p className='text-sm font-semibold text-primary mb-2'>{time}</p>
			<h4 className='font-semibold text-foreground mb-1'>{title}</h4>
			<p className='text-sm text-muted-foreground'>{description}</p>
		</div>
	)
}

export default Hero
