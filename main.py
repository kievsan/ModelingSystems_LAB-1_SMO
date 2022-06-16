# Моделирование систем
# Лаб/раб №1
# Имитационное моделирование СМО

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk


# ГРАФИКИ
def drawTimes(ax, v1, v2, v3, N):
    # соединим линией время прихода заявки и время ее исполнения:
    ax.hlines(y=N, xmin=v1, xmax=v2, color='grey', alpha=0.4)
    # время прихода заявок:
    ax.scatter(v1, N, color='skyblue', alpha=1, label="t")  # alpha - прозрачность
    # время исполнения:
    ax.scatter(v2, N, color='green', alpha=0.4, label="tau")
    # сетка:
    ax.grid(True)


def linePlot(ax, x_data, y_data, color="green", label=""):
    # линейный график:
    ax.plot(x_data, y_data, lw=2, color=color, alpha=1, label=label)
    # сетка:
    ax.grid(True)


def doModeling(entries):
    """
    МОДЕЛИРОВАНИЕ (ЛОГИКА)
    :param entries:  входные данные из формы ввода;
    :return: no.
    """

    """
        Массив каналов, каждый элемент - время завершения исполнения очередной заявки,
        что позволит считать канал доступным, если время истекло,
        и построить график для каждого канала:
    """
    channels = [[0.0]]
    # Очередь:
    queueTime = [0.0]  # время по оси X для построения графика очереди
    queueCount = [0]  # глубина очереди на момент времени из queueTime
    queue = [0]  # сама очередь для хранения заявок. метод FIFO
    # Отказы (аналогично):
    declineTime = [0.0]
    declineCount = [0]
    # Цвета графиков каждому каналу:
    colors = ["blue", "purple", "pink", "magenta"]

    # Расчетные массивы:
    t = [0]
    tau = [0]
    N = [0]  # Кол-во заявок на каждый момент времени (без range(1, N))
    # На основе t & tau моменты времени:
    startTime = [0]
    endTime = [0]

    # Инициализируем потоки (каналы обслуживания) по заданному n:
    for l in range(0, int(entries['n'].get())):
        channels.append([0.0])

    # t & tau формируем:
    t = np.random.lognormal(float(entries['λ'].get()), float(entries['σ(λ)'].get()), int(entries['N'].get()) + 1)
    tau = np.random.lognormal(float(entries['μ'].get()), float(entries['σ(μ)'].get()), int(entries['N'].get()) + 1)

    # Моделирование:
    for i in range(1, int(entries['N'].get()) + 1):
        # Время для графиков и расчетов
        startTime.append(startTime[i - 1] + t[i])
        endTime.append(startTime[i] + tau[i])
        """
            Добавляем все заявки в очередь. Любая заявка идет в конец очереди. В массив кладем индекс заявки.
            Все ее характеристики будем получать из других массивов по индексу.
            Если каналы свободны, то заявка пойдет сразу на обработку, если каналы заняты - очередь будет расти.
        """
        queue.append(i)
        order = queue[1]  # Берем первую заявку из очереди FIFO
        queueStartTime = startTime[i]
        """
            Распределяем по каналам обслуживания. Проверяем доступность каналов в каждый момент времени прихода
            новой заявки! Pазмещать заявку в случае свободного канала будем из очереди:
        """
        for l in range(0, int(entries['n'].get())):
            # Если в очереди только нулевой элемент - выходим из цикла, очередь пуста. safety check
            if len(queue) == 1:
                break
            """
                Проверяем, закончил ли канал обработку предыдущей заявки
                Если на время прихода заявки время обработки предыдущей заявки истекло,
                значит канал свободен для размещения. Иначе проверяем след канал. 
                Если все каналы заняты, двигаемся дальше, а заявка остается в очереди, которая будет расти
            """
            if startTime[i] > channels[l][len(channels[l]) - 1]:
                """
                    Устанавливаем новое время окончания обработки заявки каналом
                    Если заявка из очереди пришла после завершения обработки каналом прошлой заявки,
                    то время окончания обработки заявки будет считаться от момента прихода заявки
                    (канал простаивал, пришла заявка, время окончания ее обработки t+tau=endTime).
                    Иначе время завершения будет осчитываться от времни завершения выполнения предыдущей заявки
                    (t+tau предыдущ заявки + tau текущей)
                """
                if startTime[order] > channels[l][len(channels[l]) - 1]:
                    queueStartTime = startTime[order]
                    channels[l].append(endTime[order])
                else:
                    queueStartTime = channels[l][len(channels[l]) - 1]
                    channels[l].append(channels[l][len(channels[l]) - 1] + tau[order])
                queue.pop(1)    # Поскольку разместили элемент в канал обработки - убираем его из очереди

        # Если очередь превышает допустимую длину, добавляем отказ и убираем заявку из очереди:
        if len(queue) > int(entries['L'].get()) + 1:
            # Увеличиваем кол-во отказов
            # Текущее значение для графика отказов:
            declineCount.append(declineCount[len(declineCount) - 1])
            declineTime.append(startTime[i])
            # Новое значение зубчика:
            declineCount.append(declineCount[len(declineCount) - 1] + 1)
            declineTime.append(startTime[i])
            queue.pop(len(queue) - 1)   # Удаляем отказ из очереди

        # График очереди
        # Текущее значение для зубчика графика очереди:
        queueCount.append(queueCount[len(queueCount) - 1])
        queueTime.append(queueStartTime)
        # Новое значение зубчика и количество -1 поскольку мы не считаем 0-й элемент:
        queueCount.append(len(queue) - 1)
        queueTime.append(queueStartTime)

        N.append(i)
        # print(N[i], t[i], tau[i], startTime[i], endTime[i])

    # После прихода последней заявки раскладываем остатки очереди по каналам:
    while len(queue) > 1:
        # Находим свободный канал
        freeChannel = 0
        for i in range(0, int(entries['n'].get())):
            # свободный канал - канал с ближайшим завершением работы (в него определим заявку)
            if channels[i][len(channels[i]) - 1] < channels[freeChannel][len(channels[freeChannel]) - 1]:
                freeChannel = i

        # Нулевая заявка была пустышкой, поэтому дойдя до 1 элемента в очереди - выходим
        if len(queue) > 1:
            sTime = channels[freeChannel][len(channels[freeChannel]) - 1]
            channels[freeChannel].append(sTime + tau[queue[1]])
            declineCount.append(declineCount[len(declineCount) - 1])
            declineTime.append(sTime + tau[queue[1]])
            queue.pop(1)
            # График очереди
            # Текущее значение для зубчиков:
            queueCount.append(queueCount[len(queueCount) - 1])
            queueTime.append(sTime)
            # Новое значение зубчика (количество -1: без 0-го элемента)
            queueCount.append(len(queue) - 1)
            queueTime.append(sTime)

    # Выделяем 3 области для графиков:
    fig, axarr = plt.subplots(3, sharex=True)
    # заголовки:
    fig.suptitle(workTitle, fontsize=12, fontname='Times New Roman', color='gray')
    axarr[0].set_title("Orders Processing with " + str(int(entries['n'].get())) + " Chanels", loc='left')
    for i in range(0,3):
        axarr[i].set_xlabel('Time')
        axarr[i].set_ylabel('Orders')
    # размерность:
    axarr[0].set_ylim(0, N[len(N) - 1] + 10)
    linePlot(axarr[0], startTime, N, "green", "Orders In")
    color = 0
    # обработанные очереди:
    for channel in channels:
        if len(channel) > 1:
            linePlot(axarr[0], channel, range(0, len(channel)), colors[color], label="Chanel - " + str(color + 1))
            color += 1
    # отказы:
    linePlot(axarr[0], declineTime, declineCount, "red", label="Declines")
    axarr[0].legend(loc='upper left')

    # время заявок:
    axarr[1].set_ylim(0, N[len(N) - 1] + 10)
    drawTimes(axarr[1], startTime, endTime, tau, N)
    axarr[1].legend(loc='upper left')

    # область очереди:
    axarr[2].set_ylim(0, int(entries['L'].get()) * 1.3)
    linePlot(axarr[2], queueTime, queueCount, "orange", label="Queue")
    axarr[2].legend(loc='upper left')

    plt.show()    # все выводим на экран

    # fig.savefig('Lab1_ModelingSystems.jpg')


def makeForm(widget, fields):
    """
    Cоздание простой формы для входных данных
    :param widget: окно ввода;
    :param fields: типы входных данных;
    :return:   входные данные из формы.
    """
    entries = {}
    for field in fields:
        row = tk.Frame(widget)
        name = tk.Label(row, width=22, text=field + ": ", anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, "0")
        row.pack(side=tk.TOP,
                 fill=tk.X,
                 padx=5,
                 pady=5)
        name.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT,
                 expand=tk.YES,
                 fill=tk.X)
        entries[field] = ent
    return entries


if __name__ == '__main__':
    workTitle = 'Лаб/раб №1. Моделирование систем'
    fields = ('n', 'λ', 'σ(λ)', 'μ', 'σ(μ)', 'L', 'N')
    widget = tk.Tk()
    widget.title(workTitle)
    entries = makeForm(widget, fields)
    b2 = tk.Button(widget, text='Моделирование',
                   command=(lambda e=entries: doModeling(e)))
    b2.pack(side=tk.LEFT, padx=5, pady=5)
    b3 = tk.Button(widget, text='Выход', command=widget.quit)
    b3.pack(side=tk.RIGHT, padx=5, pady=5)
    widget.mainloop()
