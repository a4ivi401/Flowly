import { CheckCircle2 } from "lucide-react";

const HowItWorks = () => {
  const steps = [
    {
      number: "01",
      title: "Додайте задачі",
      description: "Просто внесіть список справ на день або імпортуйте з інших систем"
    },
    {
      number: "02",
      title: "AI проаналізує",
      description: "Штучний інтелект оцінить складність, час виконання та пріоритети"
    },
    {
      number: "03",
      title: "Отримайте розклад",
      description: "Система створить оптимальний план дня з урахуванням ваших можливостей"
    },
    {
      number: "04",
      title: "Виконуйте та адаптуйте",
      description: "Працюйте за планом, а AI допоможе коригувати його в реальному часі"
    }
  ];

  return (
    <section id="how" className="py-20 px-6 bg-gradient-to-b from-background to-background/50">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Як це працює
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Чотири простих кроки до ефективного планування вашого дня
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {steps.map((step, index) => (
            <div 
              key={index}
              className="relative"
            >
              <div className="flex flex-col items-center text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-2xl font-bold text-white mb-4 shadow-lg">
                  {step.number}
                </div>
                <h3 className="text-xl font-semibold mb-3 text-foreground">
                  {step.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed">
                  {step.description}
                </p>
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-8 left-[calc(50%+2rem)] w-[calc(100%-4rem)] h-0.5 bg-gradient-to-r from-primary/50 to-transparent" />
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <div className="inline-flex items-center gap-2 text-primary font-medium">
            <CheckCircle2 className="w-5 h-5" />
            <span>Безкоштовна пробна версія на 14 днів</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
