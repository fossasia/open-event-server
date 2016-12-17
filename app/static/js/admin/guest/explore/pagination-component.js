Vue.component('pagination', {
    template: "<div class=\"VuePagination\"> <ul v-show=\"totalPages>1\" class=\"pagination VuePagination__pagination\"> <li class=\"VuePagination__pagination-item VuePagination__pagination-item-prev-chunk\" v-bind:class=\"allowedChunk(-1)?'':'disabled'\"> <a href=\"javascript:void(0);\" v-on:click=\"prevChunk()\">&lt;&lt;</a> </li> <li class=\"VuePagination__pagination-item VuePagination__pagination-item-prev-page\" v-bind:class=\"allowedPage(page-1)?'':'disabled'\"> <a href=\"javascript:void(0);\" v-on:click=\"prev()\">&lt;</a> </li> <li class=\"VuePagination__pagination-item\" v-for=\"page in pages\" v-bind:class=\"isActive(page)?'active':''\"> <a href=\"javascript:void(0);\" v-on:click=\"setPage(page)\">{{page}}</a> </li> <li class=\"VuePagination__pagination-item VuePagination__pagination-item-next-page\" v-bind:class=\"allowedPage(page + 1)?'':'disabled'\"> <a href=\"javascript:void(0);\" v-on:click=\"next()\">&gt;</a> </li> <li class=\"VuePagination__pagination-item VuePagination__pagination-item-next-chunk\" v-bind:class=\"allowedChunk(1)?'':'disabled'\"> <a href=\"javascript:void(0);\" v-on:click=\"nextChunk()\">&gt;&gt;</a> </li> </ul> <p v-if=\"records>0\" class=\"VuePagination__count\">{{count}}</p> </div>",
    data: function () {
        return {
            page: 1
        };
    },
    props: {
        records: {
            type: Number,
            required: true
        },
        perPage: {
            type: Number,
            required: false,
            default: 25
        },
        chunk: {
            type: Number,
            required: false,
            default: 10
        },
        countText: {
            type: String,
            required: false,
            default: '{count} records'
        }
    },
    computed: {
        pages: function () {

            if (!this.records)
                return [];

            return range(this.paginationStart, this.pagesInCurrentChunk);
        },
        totalPages: function () {
            return this.records ? Math.ceil(this.records / this.perPage) : 1;
        },
        totalChunks: function () {
            return Math.ceil(this.totalPages / this.chunk);
        },
        currentChunk: function () {
            return Math.ceil(this.page / this.chunk);
        },
        paginationStart: function () {
            return ((this.currentChunk - 1) * this.chunk) + 1;
        },
        count: function () {
            return this.countText.replace('{count}', this.records);
        },
        pagesInCurrentChunk: function () {
            return this.paginationStart + this.chunk <= this.totalPages ?
                this.chunk :
                this.totalPages - this.paginationStart + 1;
        }
    },
    methods: {
        setPage: function (page) {
            if (this.allowedPage(page)) {
                this.page = page;
                this.$emit('change', 'page', page);
                return true;
            }
            return false;
        },
        next: function () {
            return this.setPage(this.page + 1);
        },
        prev: function () {
            return this.setPage(this.page - 1);
        },
        nextChunk: function () {
            return this.setChunk(1);
        },
        prevChunk: function () {
            return this.setChunk(-1);
        },
        setChunk: function (direction) {
            this.setPage((((this.currentChunk - 1) + direction) * this.chunk) + 1);
        },
        allowedPage: function (page) {
            return page >= 1 && page <= this.totalPages;
        },
        allowedChunk: function (direction) {
            return (direction == 1 && this.currentChunk < this.totalChunks)
                || (direction == -1 && this.currentChunk > 1);
        },
        isActive: function (page) {
            return this.page == page;
        }
    }
});


function range(start, count) {
    return Array.apply(0, new Array(count))
        .map(function (element, index) {
            return index + start;
        });
}
