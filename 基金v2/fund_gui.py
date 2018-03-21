import tkinter as tk

def fund_gui(total_rank):
    root = tk.Tk()
    root.title('股票基金评分排名')

    def entry_Return(event):
        button_action()
    entry = tk.Entry(root)
    entry.bind('<Return>', entry_Return)
    entry.grid(row=0, column=2)

    def button_action():
        try:
            if int(entry.get()) >= len(total_rank):
                label['text'] = 'Sorry!No found.'
            else:
                detail = total_rank[int(entry.get())]
                label['text'] = 'rank:' + entry.get() + '\n'\
                                + '基金代码:' + str(detail['基金代码']) + '\n'\
                                + '基金简称:' + str(detail['基金简称']) + '\n'\
                                + '日增长率:' + str(detail['日增长率']) + '%\n'\
                                + '近1周:' + str(detail['近1周']) + '%\n'\
                                + '近1月:' + str(detail['近1月']) + '%\n'\
                                + '近3月:' + str(detail['近3月']) + '%\n'\
                                + '近6月:' + str(detail['近6月']) + '%\n'\
                                + '近1年:' + str(detail['近1年']) + '%\n'\
                                + '近2年:' + str(detail['近2年']) + '%\n'\
                                + '手续费:' + str(detail['手续费']) + '%\n'\
                                + '赎回费率:' + str(detail['赎回费率']) + '%'
                                               
        except ValueError:
            label['text'] = "Please input correct 'Number' !"
    button = tk.Button(root, text='Check', command=button_action)
    button.grid(row=0, column=3)

    def button_code_action():
        code = ''
        try:
            int(entry.get())
            code = entry.get()
        except ValueError:
            code = 0
        detail = None
        rank_index = '---'
        for index,fund in enumerate(total_rank):
            if str(fund['基金代码']) == code:
                detail = fund
                rank_index = index
        if rank_index == '---':
            label['text'] = 'Sorry!No found.'
        else:
            label['text'] = 'rank:' + str(rank_index) + '\n'\
                            + '基金代码:' + str(detail['基金代码']) + '\n'\
                            + '基金简称:' + str(detail['基金简称']) + '\n'\
                            + '日增长率:' + str(detail['日增长率']) + '%\n'\
                            + '近1周:' + str(detail['近1周']) + '%\n'\
                            + '近1月:' + str(detail['近1月']) + '%\n'\
                            + '近3月:' + str(detail['近3月']) + '%\n'\
                            + '近6月:' + str(detail['近6月']) + '%\n'\
                            + '近1年:' + str(detail['近1年']) + '%\n'\
                            + '近2年:' + str(detail['近2年']) + '%\n'\
                            + '手续费:' + str(detail['手续费']) + '%\n'\
                            + '赎回费率:' + str(detail['赎回费率']) + '%'
            
    button_code = tk.Button(root, text='Code', command=button_code_action)
    button_code.grid(row=0, column=4)

    label = tk.Label(root)
    label.grid(row=1, column=2, columnspan=3)

    root.mainloop()
