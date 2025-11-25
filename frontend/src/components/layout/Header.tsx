import { Button } from '@/components/ui/button'

const Header = () => {
	return (
		<header className='fixed top-0 left-0 right-0 z-50 bg-card/80 backdrop-blur-md border-b border-border'>
			<div className='container mx-auto px-6 py-4'>
				<div className='flex items-center justify-between'>
					<div className='flex items-center gap-2'>
						<h1 className='text-2xl font-bold text-primary'>FLOWLY</h1>
						<span className='text-sm text-muted-foreground'>AI time OS</span>
					</div>

					<nav className='hidden md:flex items-center gap-8'>
						<a
							href='#features'
							className='text-foreground hover:text-primary transition-colors'
						>
							Можливості
						</a>
						<a
							href='#how'
							className='text-foreground hover:text-primary transition-colors'
						>
							Як працює
						</a>
					</nav>

					<Button variant='hero' size='lg' asChild>
						Запросити демо
					</Button>
				</div>
			</div>
		</header>
	)
}

export default Header
