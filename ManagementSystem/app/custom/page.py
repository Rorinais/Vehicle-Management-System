from django.utils.safestring import mark_safe


class Page(object):

    def __init__(self, request, queryset, page_size=10, page_param="page", plus=5):
        page = request.GET.get(page_param, "1")
        if page.isdecimal():
            page = int(page)
        else:
            page = 1
        self.page = page
        self.page_size = page_size

        self.start = (page - 1) * page_size
        self.end = page * page_size
        self.page_queryset = queryset[self.start:self.end]

        total_count = queryset.count()

        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1

        self.total_page_count = total_page_count
        self.plus = plus

    def html(self):

        if self.total_page_count <= 2 * self.plus + 1:
            start_page = 1
            end_page = self.total_page_count
        else:
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus
            else:
                if (self.page + self.plus) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        page_str_list = []
        page_str_list.append("<li><a href='?page={}'>首页</a></li>".format(1))
        if self.page > 1:
            prev = "<li><a href='?page={}'>上一页</a></li>".format(self.page - 1)
        else:
            prev = "<li><a href='?page={}'>上一页</a></li>".format(1)
        page_str_list.append(prev)

        for i in range(start_page, end_page + 1):
            if i == self.page:
                ele = "<li class='active'><a href='?page={}'>{}</a></li>".format(i, i)
            else:
                ele = "<li><a href='?page={}'>{}</a></li>".format(i, i)
            page_str_list.append(ele)

        if self.page < self.total_page_count:
            prev = "<li><a href='?page={}'>下一页</a></li>".format(self.page + 1)
        else:
            prev = "<li><a href='?page={}'>下一页</a></li>".format(self.total_page_count)
        page_str_list.append(prev)
        page_str_list.append("<li><a href='?page={}'>尾页</a></li>".format(self.total_page_count))

        page_string = mark_safe("".join(page_str_list))
        return page_string
