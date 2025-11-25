import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { CalendarIcon, Loader2 } from "lucide-react";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { Task } from "@/api";

const taskFormSchema = z.object({
  title: z.string().min(1, "Назва обов'язкова").max(255, "Назва занадто довга"),
  description: z.string().optional(),
  priority: z.number().min(1).max(3),
  duration_minutes: z.number().min(1, "Тривалість має бути більше 0").optional().or(z.literal(0)),
  deadline: z.date().optional(),
  status: z.enum(["pending", "in_progress", "completed", "cancelled"]).optional(),
});

type TaskFormValues = z.infer<typeof taskFormSchema>;

interface TaskFormProps {
  task?: Task;
  onSubmit: (data: Omit<TaskFormValues, 'deadline'> & { deadline?: string }) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}

const priorityOptions = [
  { value: 1, label: "High" },
  { value: 2, label: "Medium" },
  { value: 3, label: "Low" },
];

const statusOptions = [
  { value: "pending", label: "Очікує" },
  { value: "in_progress", label: "В процесі" },
  { value: "completed", label: "Завершено" },
  { value: "cancelled", label: "Скасовано" },
];

export function TaskForm({ task, onSubmit, onCancel, isSubmitting }: TaskFormProps) {
  const isEditing = !!task;

  const form = useForm<TaskFormValues>({
    resolver: zodResolver(taskFormSchema),
    defaultValues: {
      title: task?.title || "",
      description: task?.description || "",
      priority: task?.priority || 3,
      duration_minutes: task?.duration_minutes || 0,
      deadline: task?.deadline ? new Date(task.deadline) : undefined,
      status: task?.status || "pending",
    },
  });

  const handleSubmit = (data: TaskFormValues) => {
    const submitData: any = {
      title: data.title,
      priority: data.priority,
    };

    // Додаємо опціональні поля тільки якщо вони заповнені
    if (data.description && data.description.trim()) {
      submitData.description = data.description.trim();
    }
    
    if (data.duration_minutes && data.duration_minutes > 0) {
      submitData.duration_minutes = data.duration_minutes;
    }
    
    if (data.deadline) {
      submitData.deadline = data.deadline.toISOString();
    }
    
    // Status відправляємо ТІЛЬКИ при редагуванні
    if (isEditing && data.status) {
      submitData.status = data.status;
    }
    
    onSubmit(submitData);
  };

  return (
    <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="title">Назва *</Label>
        <Input
          id="title"
          {...form.register("title")}
          placeholder="Введіть назву задачі"
          className={form.formState.errors.title ? "border-destructive" : ""}
        />
        {form.formState.errors.title && (
          <p className="text-sm text-destructive">{form.formState.errors.title.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Опис</Label>
        <Textarea
          id="description"
          {...form.register("description")}
          placeholder="Опишіть задачу детальніше"
          rows={3}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="priority">Пріоритет</Label>
        <Select
          value={form.watch("priority")?.toString()}
          onValueChange={(value) => form.setValue("priority", parseInt(value))}
        >
          <SelectTrigger>
            <SelectValue placeholder="Оберіть пріоритет" />
          </SelectTrigger>
          <SelectContent>
            {priorityOptions.map((option) => (
              <SelectItem key={option.value} value={option.value.toString()}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="duration_minutes">Тривалість (хвилини)</Label>
        <Input
          id="duration_minutes"
          type="number"
          {...form.register("duration_minutes", { valueAsNumber: true })}
          placeholder="30"
          min="1"
          className={form.formState.errors.duration_minutes ? "border-destructive" : ""}
        />
        {form.formState.errors.duration_minutes && (
          <p className="text-sm text-destructive">{form.formState.errors.duration_minutes.message}</p>
        )}
      </div>

      <div className="space-y-2">
        <Label>Дедлайн</Label>
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              className={cn(
                "w-full justify-start text-left font-normal",
                !form.watch("deadline") && "text-muted-foreground"
              )}
            >
              <CalendarIcon className="mr-2 h-4 w-4" />
              {form.watch("deadline") ? (
                format(form.watch("deadline")!, "dd.MM.yyyy")
              ) : (
                <span>Оберіть дату</span>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="single"
              selected={form.watch("deadline")}
              onSelect={(date) => form.setValue("deadline", date)}
              initialFocus
              className="p-3 pointer-events-auto"
            />
          </PopoverContent>
        </Popover>
      </div>

      {isEditing && (
        <div className="space-y-2">
          <Label htmlFor="status">Статус</Label>
          <Select
            value={form.watch("status")}
            onValueChange={(value: any) => form.setValue("status", value)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Оберіть статус" />
            </SelectTrigger>
            <SelectContent>
              {statusOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="flex gap-3 pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          className="flex-1"
          disabled={isSubmitting}
        >
          Скасувати
        </Button>
        <Button type="submit" className="flex-1" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Збереження...
            </>
          ) : isEditing ? (
            "Зберегти зміни"
          ) : (
            "Створити задачу"
          )}
        </Button>
      </div>
    </form>
  );
}
