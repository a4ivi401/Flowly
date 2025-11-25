import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient, type Task } from "@/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { useToast } from "@/hooks/use-toast";
import { TaskForm } from "@/components/TaskForm";
import {
  Plus,
  Loader2,
  Trash2,
  Edit,
  Calendar,
  Clock,
  AlertCircle,
  Sparkles,
  CheckCircle2,
} from "lucide-react";
import { format } from "date-fns";
import { Link } from "react-router-dom";

const priorityConfig = {
  1: { label: "High", color: "destructive" },
  2: { label: "Medium", color: "accent" },
  3: { label: "Low", color: "primary" },
} as const;

const statusConfig = {
  pending: { label: "Pending", color: "secondary" },
  in_progress: { label: "In Progress", color: "default" },
  completed: { label: "Completed", color: "default" },
  cancelled: { label: "Cancelled", color: "outline" },
} as const;

interface PlannedTask {
  task_id: number;
  priority_rank: number;
  planned_start: string;
  planned_end: string;
  duration_minutes: number;
  note: string | null;
  task: Task;
}

interface PlanResponse {
  generated_at: string;
  timezone: string;
  tasks: PlannedTask[];
}

const TasksPage = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [viewingTask, setViewingTask] = useState<Task | null>(null);
  const [deletingTaskId, setDeletingTaskId] = useState<number | null>(null);
  const [isOptimizeFormOpen, setIsOptimizeFormOpen] = useState(false);
  
  // Optimize form state
  const [timezone, setTimezone] = useState("Europe/Kyiv");
  const [workdayHours, setWorkdayHours] = useState(8);
  const [longBreakMinutes, setLongBreakMinutes] = useState(60);
  const [shortBreakMinutes, setShortBreakMinutes] = useState(15);

  const { data: tasks = [], isLoading, error } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => apiClient.getTasks(),
  });

  const { data: plan, isLoading: isPlanLoading } = useQuery({
    queryKey: ["todayPlan"],
    queryFn: () => apiClient.getTodayPlan(),
  });

  const createMutation = useMutation({
    mutationFn: (task: any) => apiClient.createTask(task),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast({
        title: "Задачу створено",
        description: "Нову задачу успішно додано до списку",
      });
      setIsFormOpen(false);
    },
    onError: (error: Error) => {
      toast({
        title: "Помилка",
        description: `Не вдалося створити задачу: ${error.message}`,
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, task }: { id: number; task: any }) => apiClient.updateTask(id, task),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast({
        title: "Задачу оновлено",
        description: "Зміни успішно збережено",
      });
      setIsFormOpen(false);
      setEditingTask(null);
    },
    onError: (error: Error) => {
      toast({
        title: "Помилка",
        description: `Не вдалося оновити задачу: ${error.message}`,
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: apiClient.deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      toast({
        title: "Задачу видалено",
        description: "Задачу успішно видалено зі списку",
      });
      setDeletingTaskId(null);
    },
    onError: (error: Error) => {
      toast({
        variant: "destructive",
        title: "Помилка",
        description: error.message || "Не вдалося видалити задачу",
      });
    },
  });

  const planTodayMutation = useMutation({
    mutationFn: apiClient.planToday,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["todayPlan"] });
      setIsOptimizeFormOpen(false);
      toast({
        title: "План створено",
        description: `Заплановано ${data.tasks.length} задач на сьогодні`,
      });
    },
    onError: (error: Error) => {
      toast({
        variant: "destructive",
        title: "Помилка",
        description: error.message || "Не вдалося створити план",
      });
    },
  });

  const completeTaskMutation = useMutation({
    mutationFn: (taskId: number) =>
      apiClient.updateTask(taskId, { status: "completed" }),
    onSuccess: (updatedTask) => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["todayPlan"] });

      toast({
        title: "Задачу виконано",
        description: `"${updatedTask.title}" позначено як виконану`,
      });
    },
    onError: (error: Error) => {
      toast({
        variant: "destructive",
        title: "Помилка",
        description: error.message || "Не вдалося оновити статус",
      });
    },
  });

  const handleFormSubmit = (data: any) => {
    if (editingTask && editingTask.id) {
      updateMutation.mutate({ id: editingTask.id, task: data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleDeleteTask = (id: number) => {
    setDeletingTaskId(id);
  };

  const confirmDelete = () => {
    if (deletingTaskId !== null) {
      deleteMutation.mutate(deletingTaskId);
    }
  };

  const handleViewTask = (task: Task) => {
    setViewingTask(task);
  };

  const handleEditFromView = () => {
    if (viewingTask) {
      setEditingTask(viewingTask);
      setViewingTask(null);
      setIsFormOpen(true);
    }
  };

  const handleCloseView = () => {
    setViewingTask(null);
  };

  const handleCloseForm = () => {
    setIsFormOpen(false);
    setEditingTask(null);
  };

  const handleOptimize = () => {
    planTodayMutation.mutate({
      timezone,
      workday_hours: workdayHours,
      long_break_minutes: longBreakMinutes,
      short_break_minutes: shortBreakMinutes,
    });
  };

  const handleCompleteTask = (taskId: number) => {
    completeTaskMutation.mutate(taskId);
  };

  const formatTime = (isoString: string) => {
    try {
      return format(new Date(isoString), "HH:mm");
    } catch {
      return isoString;
    }
  };

  const formatDeadline = (deadline: string | null | undefined) => {
    if (!deadline) return null;
    return new Date(deadline).toLocaleDateString("uk-UA");
  };

  const formatDuration = (minutes: number | null | undefined) => {
    if (!minutes) return null;
    return `${minutes} хв`;
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border bg-card/80 backdrop-blur-md">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-3 sm:gap-4">
            <Link 
              to="/" 
              className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent hover:opacity-80 transition-opacity"
            >
              Flowly
            </Link>
            <div className="h-6 w-px bg-border hidden sm:block" />
            <h1 className="text-xl sm:text-2xl font-semibold text-foreground">Планування завдань</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <Tabs defaultValue="tasks" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8">
            <TabsTrigger value="tasks">Мої задачі</TabsTrigger>
            <TabsTrigger value="plan">План на день</TabsTrigger>
          </TabsList>

          {/* Tab 1: Мої задачі */}
          <TabsContent value="tasks" className="space-y-6">
            <div className="flex justify-between items-center flex-wrap gap-3">
              <h2 className="text-xl font-semibold">Список задач</h2>
              <div className="flex gap-3">
                <Button
                  variant="hero"
                  onClick={() => setIsOptimizeFormOpen(true)}
                >
                  <Sparkles className="mr-2 h-5 w-5" />
                  Оптимізувати задачі
                </Button>
                <Button
                  variant="default"
                  onClick={() => {
                    setEditingTask(null);
                    setIsFormOpen(true);
                  }}
                >
                  <Plus className="mr-2 h-5 w-5" />
                  Додати задачу
                </Button>
              </div>
            </div>

            {isLoading && (
              <div className="flex items-center justify-center min-h-[60vh]">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            )}

            {error && (
              <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                  <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
                  <p className="text-lg text-muted-foreground">
                    Не вдалося завантажити задачі
                  </p>
                  <p className="text-sm text-muted-foreground mt-2">
                    {error instanceof Error ? error.message : "Невідома помилка"}
                  </p>
                </div>
              </div>
            )}

            {!isLoading && !error && tasks && tasks.length === 0 && (
              <div className="flex items-center justify-center min-h-[60vh]">
                <div className="text-center">
                  <p className="text-lg text-muted-foreground mb-4">
                    Немає задач для відображення
                  </p>
                  <Button
                    variant="default"
                    onClick={() => {
                      setEditingTask(null);
                      setIsFormOpen(true);
                    }}
                  >
                    <Plus className="mr-2 h-5 w-5" />
                    Додати першу задачу
                  </Button>
                </div>
              </div>
            )}

            {!isLoading && !error && tasks && tasks.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {tasks.map((task) => {
                  const priority = task.priority as keyof typeof priorityConfig;
                  const priorityInfo =
                    priorityConfig[priority] || priorityConfig[2];
                  const isCompleted = task.status === "completed";

                  return (
                    <Card
                      key={task.id}
                      className={`cursor-pointer transition-all hover:shadow-lg hover:scale-[1.02] ${
                        isCompleted ? "opacity-50 bg-muted/30" : ""
                      }`}
                      onClick={() => handleViewTask(task)}
                      style={{
                        borderLeft: `4px solid hsl(var(--${priorityInfo.color}))`,
                      }}
                    >
                      <CardHeader>
                        <div className="flex items-start justify-between gap-4">
                          <CardTitle className={`text-xl ${isCompleted ? "line-through text-muted-foreground" : ""}`}>
                            {task.title}
                          </CardTitle>
                          <div className="flex gap-2 shrink-0">
                            {isCompleted && (
                              <Badge variant="outline" className="gap-1">
                                <CheckCircle2 className="h-3 w-3" />
                                Виконано
                              </Badge>
                            )}
                            <Badge variant={priorityInfo.color as any}>
                              {priorityInfo.label}
                            </Badge>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {task.description && (
                          <p className={`text-sm mb-4 ${isCompleted ? "text-muted-foreground/70" : "text-muted-foreground"}`}>
                            {task.description}
                          </p>
                        )}
                        <div className="flex flex-wrap items-center justify-between gap-4">
                          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                            {task.duration_minutes && (
                              <div className="flex items-center gap-1">
                                <Clock className="h-4 w-4" />
                                <span>{formatDuration(task.duration_minutes)}</span>
                              </div>
                            )}
                            {task.deadline && (
                              <div className="flex items-center gap-1">
                                <Calendar className="h-4 w-4" />
                                <span>{formatDeadline(task.deadline)}</span>
                              </div>
                            )}
                          </div>
                          {!isCompleted && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={(e) => {
                                e.stopPropagation();
                                handleCompleteTask(task.id!);
                              }}
                              className="gap-1"
                            >
                              <CheckCircle2 className="h-4 w-4" />
                              Виконано
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </TabsContent>

          {/* Tab 2: План на день */}
          <TabsContent value="plan" className="space-y-6">
            {isPlanLoading && (
              <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
                <p className="text-lg text-muted-foreground">
                  Завантаження плану...
                </p>
              </div>
            )}

            {!isPlanLoading && !plan && !planTodayMutation.isPending && (
              <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
                <Calendar className="h-16 w-16 text-muted-foreground mb-4" />
                <h2 className="text-2xl font-semibold text-foreground mb-2">
                  Немає активного плану
                </h2>
                <p className="text-muted-foreground mb-6 max-w-md">
                  Перейдіть на вкладку "Мої задачі" та натисніть "Оптимізувати задачі"
                </p>
              </div>
            )}

            {planTodayMutation.isPending && (
              <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
                <p className="text-lg text-muted-foreground">
                  Створюємо оптимальний план...
                </p>
              </div>
            )}

            {plan && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold">Оптимізований розклад</h2>
                    <p className="text-sm text-muted-foreground">
                      Згенеровано: {format(new Date(plan.generated_at), "dd.MM.yyyy HH:mm")}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Часовий пояс: {plan.timezone}
                    </p>
                  </div>
                  <Badge variant="default" className="text-base px-4 py-2">
                    {plan.tasks.length} задач
                  </Badge>
                </div>

                <div className="space-y-4">
                  {plan.tasks.map((plannedTask) => {
                    const priority = plannedTask.task.priority as keyof typeof priorityConfig;
                    const priorityInfo = priorityConfig[priority] || priorityConfig[2];
                    const status = plannedTask.task.status as keyof typeof statusConfig;
                    const statusInfo = statusConfig[status] || statusConfig.pending;
                    const isCompleted = plannedTask.task.status === "completed";

                    return (
                      <Card
                        key={plannedTask.task_id}
                        className={`transition-all hover:shadow-md ${
                          isCompleted ? "opacity-60" : ""
                        }`}
                      >
                        <CardHeader className="pb-3">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1 space-y-2">
                              <div className="flex items-center gap-2 flex-wrap">
                                <Badge variant="outline" className="text-xs">
                                  #{plannedTask.priority_rank}
                                </Badge>
                                <Badge variant={priorityInfo.color as any}>
                                  {priorityInfo.label}
                                </Badge>
                                <Badge variant={statusInfo.color as any}>
                                  {statusInfo.label}
                                </Badge>
                              </div>
                              <CardTitle className="text-xl">
                                {plannedTask.task.title}
                              </CardTitle>
                              {plannedTask.task.description && (
                                <p className="text-sm text-muted-foreground">
                                  {plannedTask.task.description}
                                </p>
                              )}
                            </div>
                            {!isCompleted && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleCompleteTask(plannedTask.task_id)}
                                disabled={completeTaskMutation.isPending}
                                className="shrink-0"
                              >
                                <CheckCircle2 className="h-4 w-4 mr-2" />
                                Виконано
                              </Button>
                            )}
                            {isCompleted && (
                              <Badge variant="default" className="shrink-0">
                                <CheckCircle2 className="h-4 w-4 mr-1" />
                                Виконано
                              </Badge>
                            )}
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="flex items-center gap-6 text-sm text-muted-foreground">
                            <div className="flex items-center gap-2">
                              <Clock className="h-4 w-4" />
                              <span>
                                {formatTime(plannedTask.planned_start)} -{" "}
                                {formatTime(plannedTask.planned_end)}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4" />
                              <span>{plannedTask.duration_minutes} хв</span>
                            </div>
                          </div>
                          {plannedTask.note && (
                            <p className="mt-3 text-sm text-muted-foreground italic">
                              Примітка: {plannedTask.note}
                            </p>
                          )}
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>

      {/* Task Form Sheet */}
      <Sheet open={isFormOpen} onOpenChange={handleCloseForm}>
        <SheetContent className="overflow-y-auto">
          <SheetHeader>
            <SheetTitle>{editingTask ? "Редагувати задачу" : "Нова задача"}</SheetTitle>
            <SheetDescription>
              {editingTask ? "Внесіть зміни до задачі" : "Заповніть форму для створення нової задачі"}
            </SheetDescription>
          </SheetHeader>
          <div className="mt-6">
            <TaskForm
              task={editingTask || undefined}
              onSubmit={handleFormSubmit}
              onCancel={handleCloseForm}
              isSubmitting={createMutation.isPending || updateMutation.isPending}
            />
          </div>
        </SheetContent>
      </Sheet>

      {/* Optimize Form Dialog */}
      <Dialog open={isOptimizeFormOpen} onOpenChange={setIsOptimizeFormOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Оптимізація задач</DialogTitle>
            <DialogDescription>
              Налаштуйте параметри для створення оптимального плану
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="timezone">Часовий пояс</Label>
              <Input
                id="timezone"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                placeholder="Europe/Kyiv"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="workday">Робочий день (годин)</Label>
              <Input
                id="workday"
                type="number"
                min="1"
                max="24"
                value={workdayHours}
                onChange={(e) => setWorkdayHours(Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="longBreak">Довга перерва (хвилин)</Label>
              <Input
                id="longBreak"
                type="number"
                min="0"
                max="120"
                value={longBreakMinutes}
                onChange={(e) => setLongBreakMinutes(Number(e.target.value))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="shortBreak">Коротка перерва (хвилин)</Label>
              <Input
                id="shortBreak"
                type="number"
                min="0"
                max="60"
                value={shortBreakMinutes}
                onChange={(e) => setShortBreakMinutes(Number(e.target.value))}
              />
            </div>
            <Button
              onClick={handleOptimize}
              disabled={planTodayMutation.isPending}
              className="w-full"
            >
              {planTodayMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Планування...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Створити план
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Task Details Dialog */}
      <Dialog open={viewingTask !== null} onOpenChange={handleCloseView}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="text-2xl">{viewingTask?.title}</DialogTitle>
            <DialogDescription>
              Детальна інформація про задачу
            </DialogDescription>
          </DialogHeader>
          {viewingTask && (
            <div className="space-y-6 py-4">
              {/* Priority and Status */}
              <div className="flex flex-wrap gap-3">
                <span 
                  className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-semibold ${
                    priorityConfig[viewingTask.priority as keyof typeof priorityConfig]?.color === "destructive" 
                      ? "bg-destructive/10 text-destructive" 
                      : priorityConfig[viewingTask.priority as keyof typeof priorityConfig]?.color === "accent" 
                      ? "bg-accent/10 text-accent-foreground" 
                      : "bg-primary/10 text-primary"
                  }`}
                >
                  <AlertCircle className="w-4 h-4 mr-2" />
                  {priorityConfig[viewingTask.priority as keyof typeof priorityConfig]?.label || "Medium"}
                </span>
                <span className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-secondary text-secondary-foreground">
                  {viewingTask.status === "pending" && "Очікує"}
                  {viewingTask.status === "in_progress" && "В процесі"}
                  {viewingTask.status === "completed" && "Завершено"}
                  {viewingTask.status === "cancelled" && "Скасовано"}
                </span>
              </div>

              {/* Description */}
              {viewingTask.description && (
                <div>
                  <h3 className="text-sm font-semibold text-muted-foreground mb-2">Опис</h3>
                  <p className="text-base text-foreground whitespace-pre-wrap">{viewingTask.description}</p>
                </div>
              )}

              {/* Details Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {viewingTask.deadline && (
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                    <Calendar className="w-5 h-5 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">Дедлайн</p>
                      <p className="text-sm font-semibold text-foreground mt-1">
                        {formatDeadline(viewingTask.deadline)}
                      </p>
                    </div>
                  </div>
                )}
                {viewingTask.duration_minutes && (
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                    <Clock className="w-5 h-5 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">Тривалість</p>
                      <p className="text-sm font-semibold text-foreground mt-1">
                        {formatDuration(viewingTask.duration_minutes)}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Timestamps */}
              <div className="pt-4 border-t space-y-2">
                <p className="text-xs text-muted-foreground">
                  Створено: {new Date(viewingTask.created_at).toLocaleString("uk-UA")}
                </p>
                <p className="text-xs text-muted-foreground">
                  Оновлено: {new Date(viewingTask.updated_at).toLocaleString("uk-UA")}
                </p>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-2">
                <Button 
                  onClick={handleEditFromView}
                  className="flex-1"
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Редагувати
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => {
                    if (viewingTask.id) {
                      setDeletingTaskId(viewingTask.id);
                      setViewingTask(null);
                    }
                  }}
                  className="flex-1"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Видалити
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deletingTaskId !== null} onOpenChange={(open) => !open && setDeletingTaskId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Підтвердження видалення</AlertDialogTitle>
            <AlertDialogDescription>
              Ви впевнені, що хочете видалити цю задачу? Цю дію не можна буде скасувати.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Скасувати</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
              Видалити
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default TasksPage;
